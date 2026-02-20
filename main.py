import tkinter as tk
from tkinter import filedialog, messagebox
from openai import OpenAI
import json
import pandas as pd
import os
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= AI ENGINE =================
def ai_analyze(text):
    prompt = f"""
You are an enterprise AI data entry system.

Task:
Analyze any unstructured input and extract structured fields automatically.

Rules:
- Auto-detect fields
- Create meaningful field names
- Max 20 fields
- Return ONLY valid JSON
- No explanation text
- No markdown

User Input:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a professional AI data extraction system."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    return response.choices[0].message.content

# ================= UI =================
class AIDataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Data Entry – Smart Automated Data Worker")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f5f5f5")

        # Title
        title = tk.Label(
            root,
            text="AI Data Entry – Smart Automated Data Worker",
            font=("Segoe UI", 22, "bold"),
            bg="#f5f5f5"
        )
        title.pack(pady=15)

        # Input Frame
        input_frame = tk.Frame(root, bg="#f5f5f5")
        input_frame.pack(pady=10)

        self.input_box = tk.Text(
            input_frame,
            height=10,
            width=120,
            font=("Consolas", 11),
            bd=1,
            relief="solid"
        )
        self.input_box.pack()

        # Buttons
        btn_frame = tk.Frame(root, bg="#f5f5f5")
        btn_frame.pack(pady=15)

        self.analyze_btn = tk.Button(
            btn_frame,
            text="Analyze Data",
            width=18,
            height=2,
            font=("Segoe UI", 10, "bold"),
            command=self.analyze
        )
        self.analyze_btn.pack(side="left", padx=15)

        self.save_btn = tk.Button(
            btn_frame,
            text="Save to Excel",
            width=18,
            height=2,
            font=("Segoe UI", 10, "bold"),
            command=self.export_excel
        )
        self.save_btn.pack(side="left", padx=15)

        # Output Title
        out_title = tk.Label(
            root,
            text="Analyzed Output",
            font=("Segoe UI", 16, "bold"),
            bg="#f5f5f5"
        )
        out_title.pack(pady=5)

        # Output Box
        self.output_box = tk.Text(
            root,
            height=18,
            width=120,
            font=("Consolas", 11),
            bd=1,
            relief="solid"
        )
        self.output_box.pack(pady=10)

        self.structured_data = {}

        # Footer
        footer = tk.Label(
            root,
            text="Powered by KD | Publisher: Deva",
            font=("Segoe UI", 9),
            bg="#f5f5f5"
        )
        footer.pack(side="bottom", pady=8)

    def analyze(self):
        raw_text = self.input_box.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showerror("Error", "Please enter data")
            return

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, "Analyzing with AI...\n")

        try:
            ai_result = ai_analyze(raw_text)
            self.structured_data = json.loads(ai_result)

            self.output_box.delete("1.0", tk.END)

            for k, v in self.structured_data.items():
                self.output_box.insert(tk.END, f"{k} : {v}\n")

        except Exception as e:
            self.output_box.delete("1.0", tk.END)
            self.output_box.insert(tk.END, f"AI Error:\n{str(e)}")

    def export_excel(self):
        if not self.structured_data:
            messagebox.showerror("Error", "No analyzed data to export")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not file_path:
            return

        df = pd.DataFrame([self.structured_data])
        df.to_excel(file_path, index=False)

        messagebox.showinfo("Success", "Excel exported successfully")

# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDataEntryApp(root)
    root.mainloop()
