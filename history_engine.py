
import json, os

DB = "history.json"

def save(data):
    hist = []
    if os.path.exists(DB):
        hist = json.load(open(DB,"r"))
    hist.append(data)
    json.dump(hist, open(DB,"w"), indent=2)

def load():
    if os.path.exists(DB):
        return json.load(open(DB,"r"))
    return []
