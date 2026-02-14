import json, os

DB_FILE = "learning_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    return json.load(open(DB_FILE))

def save_db(db):
    json.dump(db, open(DB_FILE,"w"), indent=2)

def learn_fields(data):
    db = load_db()
    for k,v in data.items():
        if k not in db:
            db[k] = {"count":1}
        else:
            db[k]["count"] += 1
    save_db(db)
