import flet as ft
import re, time, json, os, requests
from datetime import datetime
from collections import defaultdict
import pandas as pd

# =========================
# CONFIG
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # set in system env
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

# =========================
# MEMORY
# =========================
HISTORY = []
BASE_FIELDS = [
    "name","age","gender","phone","email","city","state","country","pincode",
    "product","amount","price","company","date","time","id","address",
    "dob","account","order"
]

SYNONYMS = {
    "mobile":"phone","ph":"phone","amt":"amount","cost":"amount",
    "mail":"email","location":"city"
}

SPELLING = {"amout":"amount","phon":"phone","naem":"name","adress":"address"}

# =========================
# NORMALIZATION
# =========================
def normalize(w):
    w = w.lower().strip()
    if w in SPELLING:
        w = SPELLING[w]
    if w in SYNONYMS:
        w = SYNONYMS[w]
    return w

# =========================
# OFFLINE AI ENGINE
# =========================
def offline_ai(text):
    data = defaultdict(list)

    patterns = {
        "phone": r"\b\d{10}\b",
        "pincode": r"\b\d{6}\b",
        "email": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
        "amount": r"\b\d+(?:\.\d+)?\b",
        "date": r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        "time": r"\b\d{2}:\d{2}\b"
    }

    for f,p in patterns.items():
        m = re.findall(p,text)
        if m: data[f].extend(m)

    words = re.split(r"[ ,\n]+", text)

    names = []
    for i in range(len(words)-1):
        if words[i].istitle() and words[i+1].istitle():
            names.append(words[i]+" "+words[i+1])
        elif words[i].istitle():
            names.append(words[i])

    if names: data["name"].extend(list(set(names)))

    for t in words:
        n = normalize(t)
        if n in BASE_FIELDS:
            data[n].append(t)

    return data

# =========================
# ONLINE AI ENGINE
# =========================
def online_ai(text):
    if not OPENAI_API_KEY:
        return {}

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Extract structured fields as JSON."},
            {"role": "user", "content": text}
        ],
        "temperature": 0
    }

    try:
        r = requests.post(OPENAI_URL, headers=headers, json=body, timeout=8)
        if r.status_code != 200:
            return {}
        content = r.json()["choices"][0]["message"]["content"]
        try:
            return json.loads(content)
        except:
            return {}
    except:
        return {}

# =========================
# MERGE ENGINE
# =========================
def merge(l1,l2):
    out = defaultdict(list)
    for k,v in l1.items(): out[k].extend(v)
    for k,v in l2.items():
        if isinstance(v,list): out[k].extend(v)
        else: out[k].append(str(v))
    return out

# =========================
# EXPORT
# =========================
def export_excel(data):
    flat = {}
    for k,v in data.items():
        flat[k] = ", ".join(list(set(v)))
    df = pd.DataFrame([flat])
    fn = f"ai_data_{int(time.time())}.xlsx"
    df.to_excel(fn,index=False)
    return fn

# =========================
# UI
# =========================
def main(page: ft.Page):
    page.title = "AI Data Entry – Hybrid AI System"
    page.window_width = 1100
    page.window_height = 750

    input_box = ft.TextField(label="Enter any data / text / message", multiline=True, height=180, expand=True)
    output = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    history_panel = ft.Column(scroll=ft.ScrollMode.AUTO)
    status = ft.Text("")

    def analyze(e):
        text = input_box.value
        if not text.strip(): return

        l1 = offline_ai(text)
        l2 = online_ai(text)
        result = merge(l1,l2)

        output.controls.clear()
        for k,v in result.items():
            output.controls.append(ft.Text(f"{k.upper()} : {list(set(v))}"))

        HISTORY.insert(0,result)
        if len(HISTORY)>10: HISTORY.pop()

        history_panel.controls.clear()
        for i,h in enumerate(HISTORY):
            history_panel.controls.append(ft.Text(f"{i+1}. {list(h.keys())}"))

        status.value = "✅ Data analysis successfully"
        page.update()

    def export_btn(e):
        if not HISTORY: return
        f = export_excel(HISTORY[0])
        status.value = f"✅ Excel exported: {f}"
        page.update()

    page.add(
        ft.Row([
            ft.Column([
                ft.Text("AI Data Entry – Hybrid AI System", size=22, weight="bold"),
                input_box,
                ft.Row([
                    ft.ElevatedButton("Analyze Data", on_click=analyze),
                    ft.ElevatedButton("Export Excel", on_click=export_btn)
                ]),
                status,
                ft.Divider(),
                ft.Text("Detected Fields"),
                output
            ], expand=True),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text("History (Last 10)", size=16, weight="bold"),
                history_panel
            ], width=300)
        ]),
        ft.Container(content=ft.Text("powered by KD", size=10), alignment=ft.alignment.center)
    )

ft.app(target=main)
