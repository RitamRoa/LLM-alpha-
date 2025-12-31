import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import json
import sqlite3
import os
import threading
from datetime import datetime

class QuantAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Quant Assistant Pro")
        self.root.geometry("1200x800")
        
        # FIXED Models
        self.llama_model = "Llama 3.2 1B Instruct"
        self.coder_model = "Qwen/Qwen2.5-Coder-3B-Instruct-GGUF"
        self.api_url = "http://localhost:4891/v1/chat/completions"
        
        # THREAD-SAFE DB (new connection per thread)
        self.rag_path = ""
        self.generating = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Chat (TXT)", command=self.export_chat)
        
        # Top frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 5 Menu buttons
        menus = ["Context", "Code", "Random", "Personal", "Diary"]
        self.current_menu = tk.StringVar(value="Random")
        
        for menu in menus:
            btn = tk.Button(top_frame, text=menu, width=12, bg="#4CAF50", fg="white",
                          font=("Arial", 11, "bold"), relief=tk.FLAT,
                          command=lambda m=menu: self.switch_menu(m))
            btn.pack(side=tk.LEFT, padx=3)
        
        # Status
        self.status_var = tk.StringVar(value="Ready - Thread-safe DB")
        status = tk.Label(top_frame, textvariable=self.status_var, bg="#f0f0f0")
        status.pack(side=tk.RIGHT, padx=(5,0))
        
        # Chat area
        self.chat_area = scrolledtext.ScrolledText(self.root, height=28, 
                                                 font=("Consolas", 11), bg="#1e1e1e", fg="#d4d4d4")
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))
        
        # Input
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.input_entry = tk.Entry(input_frame, font=("Arial", 13))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(input_frame, text="Send", command=self.send_message,
                 bg="#2196F3", fg="white", font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=(5,0))
        
        tk.Button(input_frame, text="📁 Add Files", command=self.add_files,
                 bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=(5,0))
        
        # Auto-setup DB on main thread
        threading.Thread(target=self.setup_db_threadsafe, daemon=True).start()
    
    def setup_db_threadsafe(self):
        """Create DB tables in background thread"""
        conn = sqlite3.connect('quant_memory.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS diary 
                       (date TEXT PRIMARY KEY, gist TEXT, full_text TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS personal 
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, timestamp TEXT)''')
        conn.commit()
        conn.close()
    
    def get_db_connection(self):
        """Thread-safe DB connection"""
        return sqlite3.connect('quant_memory.db')
    
    def switch_menu(self, menu):
        self.current_menu.set(menu)
        model = "Qwen2.5-Coder" if menu == "Code" else "Llama 3.2 1B"
        self.status_var.set(f"{menu} Mode - {model}")
        self.chat_area.insert(tk.END, f"\n🔹 {menu} Mode ({model}) 🔹\n")
        self.chat_area.see(tk.END)
    
    def send_message(self):
        query = self.input_entry.get().strip()
        if not query or self.generating: return
        
        self.input_entry.delete(0, tk.END)
        self.chat_area.insert(tk.END, f"User ({self.current_menu.get()}): {query}\n")
        self.chat_area.see(tk.END)
        
        threading.Thread(target=self.generate_response, args=(query,), daemon=True).start()
    
    def generate_response(self, query):
        self.generating = True
        try:
            handlers = {
                "Context": self.context_query,
                "Code": self.code_query,
                "Random": self.random_query,
                "Personal": self.personal_query,
                "Diary": self.diary_query
            }
            response = handlers.get(self.current_menu.get(), self.random_query)(query)
            self.root.after(0, lambda: self.display_response(response))
        finally:
            self.generating = False
    
    def display_response(self, response):
        self.chat_area.insert(tk.END, f"🤖 AI: {response}\n\n")
        self.chat_area.see(tk.END)
    
    def api_call(self, prompt, use_coder=False):
        model = self.coder_model if use_coder else self.llama_model
        try:
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": 0.1,
                "max_tokens": 1500 if use_coder else 800
            }
            resp = requests.post(self.api_url, json=payload, timeout=45)
            resp.raise_for_status()
            return resp.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}\n💡 GPT4All → Server Settings → START SERVER (port 4891)"
    
    def context_query(self, query):
        files = []
        if self.rag_path:
            for root, _, fs in os.walk(self.rag_path):
                for f in fs:
                    if f.endswith(('.csv', '.txt', '.py')):
                        files.append(f)
        context = f"Files: {len(files)} in {self.rag_path or 'No folder'}"
        use_coder = 'code' in query.lower()
        return self.api_call(f"CONTEXT (RAG): {context}\nQuery: {query}", use_coder)
    
    def code_query(self, query):
        return self.api_call(f"Qwen2.5-CODER: Generate COMPLETE working code: {query}", True)
    
    def random_query(self, query):
        use_coder = any(word in query.lower() for word in ['code', 'html', 'python', 'js'])
        return self.api_call(query, use_coder)
    
    def personal_query(self, query):
        conn = self.get_db_connection()
        cursor = conn.execute("SELECT content FROM personal ORDER BY id DESC LIMIT 3")
        memory = "; ".join([r[0] for r in cursor.fetchall()])
        conn.execute("INSERT INTO personal (content, timestamp) VALUES (?, ?)", 
                    (query, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return self.api_call(f"PERSONAL (Memory: {memory})\n{query}")
    
    def diary_query(self, query):
        today = datetime.now().strftime("%Y-%m-%d")
        conn = self.get_db_connection()
        
        if any(x in query.lower() for x in ["new entry", "save", "diary"]):
            gist = query[:80] + "..." if len(query) > 80 else query
            conn.execute("INSERT OR REPLACE INTO diary VALUES (?, ?, ?)", 
                        (today, gist, query))
            conn.commit()
            conn.close()
            return f"✅ Diary saved! {today}\nGist: {gist}"
        
        cursor = conn.execute("SELECT full_text FROM diary WHERE date=?", (today,))
        entry = cursor.fetchone()
        context = entry[0] if entry else "No diary today"
        conn.close()
        return self.api_call(f"DIARY ({today}): {context}\n{query}")
    
    def add_files(self):
        path = filedialog.askdirectory()
        if path:
            self.rag_path = path
            self.chat_area.insert(tk.END, f"📁 RAG folder added: {path}\n")
            self.chat_area.see(tk.END)
    
    def export_chat(self):
        with open("chat_export.txt", "w", encoding="utf-8") as f:
            f.write(self.chat_area.get(1.0, tk.END))
        messagebox.showinfo("Export", "Saved as chat_export.txt")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = QuantAssistant()
    app.run()
