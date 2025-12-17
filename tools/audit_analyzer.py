import json, os

LOG = "cyborg-proxy/data/audit.log"

def load():
    if not os.path.exists(LOG):
        print("No audit log found.")
        return []
    with open(LOG) as f:
        return [json.loads(l) for l in f]

def summarize(entries):
    users, roles = {}, {}
    for e in entries:
        users[e["actor"]] = users.get(e["actor"], 0) + 1
        roles[e["role"]] = roles.get(e["role"], 0) + 1

    print("=== AUDIT SUMMARY ===")
    print("Users:", users)
    print("Roles:", roles)

def timeline(entries):
    print("\n=== TIMELINE ===")
    for e in entries:
        print(f'{e["ts"]} → {e["actor"]} ({e["role"]}) {e["action"]} {e.get("filename","")}')

if __name__ == "__main__":
    data = load()
    summarize(data)
    timeline(data)