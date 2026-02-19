import tkinter as tk
from tkinter import ttk
from ai_engine import analyze_text
from excel_export import export_excel

data_store=[]

def process():
    text = box.get("1.0","end")
    result = analyze_text(text)

    if result:
        data_store.append(result)
        insert(result)

def insert(data):
    if not tree["columns"]:
        tree["columns"]=list(data.keys())
        for c in data.keys():
            tree.heading(c,text=c)
            tree.column(c,width=120)
    tree.insert("",tk.END,values=list(data.values()))

def export():
    export_excel(data_store)

def run():
    global box, tree
    root=tk.Tk()
    root.title("AI Data Entry App")
    root.geometry("900x600")

    box=tk.Text(root,height=6)
    box.pack(fill="x")

    tk.Button(root,text="Analyze",command=process).pack()
    tk.Button(root,text="Export Excel",command=export).pack()

    tree=ttk.Treeview(root,show="headings")
    tree.pack(fill="both",expand=True)

    root.mainloop()
