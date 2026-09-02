import json, subprocess, sys
out=[]; cursor=None
q='''query($c:String){repository(owner:"TauCetiProject",name:"TauCeti"){pullRequests(states:MERGED,first:100,after:$c,orderBy:{field:UPDATED_AT,direction:DESC}){pageInfo{hasNextPage endCursor} nodes{number title mergedAt additions deletions labels(first:20){nodes{name}}}}}}'''
while True:
    args=["gh","api","graphql","-f",f"query={q}"]+(["-f",f"c={cursor}"] if cursor else [])
    d=json.loads(subprocess.run(args,check=True,capture_output=True,text=True).stdout)
    pr=d["data"]["repository"]["pullRequests"]
    out+=pr["nodes"]
    print(len(out),file=sys.stderr)
    if not pr["pageInfo"]["hasNextPage"]: break
    cursor=pr["pageInfo"]["endCursor"]
json.dump(out,open(sys.argv[1],"w"))
