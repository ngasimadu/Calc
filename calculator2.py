import tkinter as tk
from tkinter import messagebox
import math
import re

class ScientificCalculator:
    def __init__(self):
        self.memory = 0
        self.history = []

    def sanitize_expression(self, expr):
        # Replace visual symbols with math logic
        expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace("π", "pi")
        
        # Auto-close parentheses
        open_count = expr.count('(')
        close_count = expr.count(')')
        if open_count > close_count:
            expr += ')' * (open_count - close_count)
            
        # Handle percentages (e.g., 200+10% -> 200+(200*10/100))
        pct_pattern = r'(\d+\.?\d*)([\+\-\*/])(\d+\.?\d*)%'
        expr = re.sub(pct_pattern, r'\1\2(\1*\3/100)', expr)
        
        # Handle standalone percentages (e.g., 50% -> 0.5)
        expr = re.sub(r'(\d+\.?\d*)%', r'(\1/100)', expr)
        
        # Handle factorials
        expr = re.sub(r'(\d+)!', r'fact(\1)', expr)
        return expr

    def evaluate(self, expression):
        if not expression: return ""
        try:
            clean_expr = self.sanitize_expression(expression)
            
            allowed_names = {
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "sqrt": math.sqrt,
                "log": math.log10,
                "ln": math.log,
                "fact": math.factorial,
                "pi": math.pi, "e": math.e, "abs": abs
            }

            # Security check for eval
            code = compile(clean_expr, "<string>", "eval")
            for name in code.co_names:
                if name not in allowed_names:
                    raise NameError(f"Access to {name} is not allowed")

            result = eval(code, {"__builtins__": {}}, allowed_names)
            
            # Format result
            if isinstance(result, float):
                result = round(result, 10)
                if result.is_integer(): result = int(result)
            
            self.history.append(f"{expression} = {result}")
            return result

        except ZeroDivisionError: return "Div by Zero"
        except Exception: return "Error"

# ------------------ GUI Implementation ------------------

class CalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.root.geometry("500x700")
        self.root.configure(bg="#121212")
        self.calc = ScientificCalculator()

        # Display Area
        self.entry = tk.Entry(root, font=("Consolas", 28), bg="#1e1e1e", fg="#ffffff",
                             borderwidth=0, justify="right", insertbackground="white")
        self.entry.pack(fill="x", padx=15, pady=(20, 5))

        # History Display (Small text above buttons)
        self.hist_label = tk.Label(root, text="History:", bg="#121212", fg="#888", font=("Arial", 10))
        self.hist_label.pack(anchor="w", padx=20)
        
        self.history_box = tk.Listbox(root, height=3, bg="#121212", fg="#00ff88", 
                                     borderwidth=0, highlightthickness=0, font=("Arial", 10))
        self.history_box.pack(fill="x", padx=20, pady=(0, 10))
        self.history_box.bind('<<ListboxSelect>>', self.on_history_select)

        # Button Frame
        self.btns_frame = tk.Frame(root, bg="#121212")
        self.btns_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.setup_buttons()
        self.setup_bindings()

    def setup_buttons(self):
        buttons = [
            ["MC", "MR", "M+", "M-", "C"],
            ["sin(", "cos(", "tan(", "π", "^"],
            ["7", "8", "9", "÷", "sqrt("],
            ["4", "5", "6", "×", "log("],
            ["1", "2", "3", "-", "ln("],
            ["0", ".", "%", "+", "="]
        ]

        for r, row in enumerate(buttons):
            self.btns_frame.grid_rowconfigure(r, weight=1)
            for c, text in enumerate(row):
                self.btns_frame.grid_columnconfigure(c, weight=1)
                self.create_button(text, r, c)

    def create_button(self, text, r, c):
        # Color Logic
        if text == "=": bg, hvr = "#00ff88", "#00cc6e"; fg = "black"
        elif text == "C": bg, hvr = "#ff3b30", "#ff6b60"; fg = "white"
        elif text in ["+", "-", "×", "÷", "%"]: bg, hvr = "#333", "#444"; fg = "#00ff88"
        elif text.isalpha() or "(" in text: bg, hvr = "#222", "#333"; fg = "#00aaff"
        else: bg, hvr = "#2d2d2d", "#3d3d3d"; fg = "white"

        btn = tk.Button(self.btns_frame, text=text, font=("Arial", 12, "bold"),
                        bg=bg, fg=fg, bd=0, activebackground=hvr, activeforeground=fg,
                        command=lambda t=text: self.handle_click(t))
        btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
        btn.bind("<Enter>", lambda e: btn.config(bg=hvr))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))

    def handle_click(self, char):
        if char == "=":
            res = self.calc.evaluate(self.entry.get())
            self.update_history()
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(res))
        elif char == "C":
            self.entry.delete(0, tk.END)
        elif char == "MC": self.calc.memory_clear()
        elif char == "MR": self.entry.insert(tk.END, str(self.calc.memory_recall()))
        elif char == "M+": 
            try: self.calc.memory_add(self.entry.get())
            except: pass
        elif char == "M-": 
            try: self.calc.memory_subtract(self.entry.get())
            except: pass
        else:
            self.entry.insert(tk.END, char)

    def update_history(self):
        self.history_box.delete(0, tk.END)
        for item in reversed(self.calc.history[-5:]): # Show last 5
            self.history_box.insert(tk.END, item)

    def on_history_select(self, event):
        if not self.history_box.curselection(): return
        index = self.history_box.curselection()[0]
        selected = self.history_box.get(index)
        # Extract the result part (after the '=')
        result_part = selected.split('=')[-1].strip()
        self.entry.delete(0, tk.END)
        self.entry.insert(tk.END, result_part)

    def setup_bindings(self):
        self.root.bind("<Return>", lambda e: self.handle_click("="))
        self.root.bind("<BackSpace>", lambda e: self.entry.delete(len(self.entry.get())-1))
        self.root.bind("<Escape>", lambda e: self.handle_click("C"))

if __name__ == "__main__":
    root = tk.Tk()
    app = CalcApp(root)
    root.mainloop()