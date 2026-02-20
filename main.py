import tkinter as tk
from tkinter import filedialog, messagebox
import openai
import json
import pandas as pd
import os
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
- Return ONLY JSON
- No explanation text

User Input:
{text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response["choices"][0]["message"]["content"]

# ================= UI APP =================
class AIDataEntryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Data Entry – Smart Automated Data Worker")
        self.root.geometry("1200x700")

        # Title
        tk.Label(root, text="AI Data Entry – Smart Automated Data Worker",
                 font=("Arial", 20, "bold")).pack(pady=10)

        # Input box
        self.input_box = tk.Text(root, height=12, width=130)
        self.input_box.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Analyze Data", width=20, command=self.analyze).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Save to Excel", width=20, command=self.export_excel).pack(side="left", padx=10)

        # Output title
        tk.Label(root, text="Analyzed Output", font=("Arial", 16, "bold")).pack(pady=5)

        # Output box
        self.output_box = tk.Text(root, height=18, width=130)
        self.output_box.pack(pady=10)

        self.structured_data = {}

        # Footer
        tk.Label(root, text="Powered by KD | Publisher: Deva", font=("Arial", 10)).pack(side="bottom", pady=5)

    def analyze(self):
        raw_text = self.input_box.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showerror("Error", "Enter some data")
            return

        try:
            ai_result = ai_analyze(raw_text)

            self.structured_data = json.loads(ai_result)

            self.output_box.delete("1.0", tk.END)

            for k, v in self.structured_data.items():
                self.output_box.insert(tk.END, f"{k} : {v}\n")

        except Exception as e:
            self.output_box.insert(tk.END, str(e))

    def export_excel(self):
        if not self.structured_data:
            messagebox.showerror("Error", "No analyzed data")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx")
        if not file_path:
            return

        df = pd.DataFrame([self.structured_data])
        df.to_excel(file_path, index=False)

        messagebox.showinfo("Success", "Excel Exported Successfully")

# ================= RUN =================
if __name__ == "__main__":
    root = tk.Tk()
    app = AIDataEntryApp(root)
    root.mainloop()
