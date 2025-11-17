import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import Counter
import heapq
import math

# ---------- Shannon-Fano ----------
def shannon_fano(symbols_probs):
    if len(symbols_probs) == 1:
        return {symbols_probs[0][0]: ''}  # ← ПУСТАЯ СТРОКА!

    symbols_probs.sort(key=lambda x: x[1], reverse=True)
    total = sum(p for _, p in symbols_probs)

    best_i = 1
    best_diff = float('inf')
    for i in range(1, len(symbols_probs)):
        left_sum = sum(p for _, p in symbols_probs[:i])
        diff = abs(left_sum - (total - left_sum))
        if diff < best_diff:
            best_diff = diff
            best_i = i

    left = symbols_probs[:best_i]
    right = symbols_probs[best_i:]

    left_codes = shannon_fano(left)
    right_codes = shannon_fano(right)

    codes = {}
    for sym, code in left_codes.items():
        codes[sym] = '0' + code
    for sym, code in right_codes.items():
        codes[sym] = '1' + code
    return codes
    
# ---------- Huffman ----------
class Node:
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq

def huffman_codes(symbols_probs):
    heap = [Node(sym, prob) for sym, prob in symbols_probs]
    heapq.heapify(heap)
    while len(heap) > 1:
        l, r = heapq.heappop(heap), heapq.heappop(heap)
        heapq.heappush(heap, Node(freq=l.freq + r.freq, left=l, right=r))
    codes = {}
    def traverse(node, prefix=""):
        if node.symbol is not None:
            codes[node.symbol] = prefix if prefix else "0"
        else:
            traverse(node.left, prefix + "0")
            traverse(node.right, prefix + "1")
    traverse(heap[0])
    return codes

# ---------- GUI ----------
class InfoTheoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №2 — Теория информации")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)

        # Верхняя панель
        top_frame = tk.Frame(root)
        top_frame.pack(pady=5, fill=tk.X)

        tk.Button(top_frame, text="Загрузить сообщение", command=self.load_file, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Код Шеннона–Фано", command=self.run_shannon, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Код Хаффмана", command=self.run_huffman, width=20).pack(side=tk.LEFT, padx=5)

        # Поле ввода текста
        text_frame = tk.LabelFrame(root, text="Исходное сообщение")
        text_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        self.text_widget = tk.Text(text_frame, height=6, wrap=tk.WORD)
        scroll = tk.Scrollbar(text_frame, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=scroll.set)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Результаты
        result_frame = tk.Frame(root)
        result_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Таблица кодов
        code_frame = tk.LabelFrame(result_frame, text="Таблица кодов")
        code_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.tree = ttk.Treeview(code_frame, columns=("Symbol", "Prob", "Code"), show="headings")
        self.tree.heading("Symbol", text="Символ")
        self.tree.heading("Prob", text="Вероятность")
        self.tree.heading("Code", text="Код")
        self.tree.column("Symbol", width=80, anchor="center")
        self.tree.column("Prob", width=100, anchor="center")
        self.tree.column("Code", width=150, anchor="center")
        vscroll = ttk.Scrollbar(code_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vscroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Метрики
        metrics_frame = tk.LabelFrame(result_frame, text="Метрики эффективности")
        metrics_frame.pack(side=tk.RIGHT, padx=(5, 0), fill=tk.Y)

        self.entropy_var = tk.StringVar(value="—")
        self.avg_len_var = tk.StringVar(value="—")
        self.redundancy_var = tk.StringVar(value="—")

        tk.Label(metrics_frame, text="Энтропия H(Z):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        tk.Label(metrics_frame, textvariable=self.entropy_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(metrics_frame, text="Средняя длина L:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        tk.Label(metrics_frame, textvariable=self.avg_len_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tk.Label(metrics_frame, text="Избыточность R:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        tk.Label(metrics_frame, textvariable=self.redundancy_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Заполним поле примером
        self.text_widget.insert(tk.END, "На дворе трава, на траве дрова. Не руби дрова на траве двора!")

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[("Text files", "*.txt")]
        )
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def get_text(self):
        return self.text_widget.get(1.0, tk.END).strip()

    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.entropy_var.set("—")
        self.avg_len_var.set("—")
        self.redundancy_var.set("—")

    def run_shannon(self):
        self._run_method("Шеннона–Фано", shannon_fano)

    def run_huffman(self):
        self._run_method("Хаффмана", huffman_codes)

    def _run_method(self, name, coder):
        text = self.get_text()
        if not text:
            messagebox.showwarning("Внимание", "Введите или загрузите текст!")
            return

        self.clear_results()

        # Статистика
        counts = Counter(text)
        total = len(text)
        symbols_probs = [(sym, cnt / total) for sym, cnt in counts.items()]
        entropy = -sum(p * math.log2(p) for _, p in symbols_probs)

        # Кодирование
        try:
            codes = coder(symbols_probs.copy())
        except RecursionError:
            messagebox.showerror("Ошибка", "Слишком большой алфавит. Попробуйте текст поменьше.")
            return

        avg_len = sum(len(codes.get(sym, "")) * p for sym, p in symbols_probs)
        redundancy = (avg_len - entropy) / avg_len if avg_len > 0 else 0

        # Обновляем интерфейс
        self.entropy_var.set(f"{entropy:.4f}")
        self.avg_len_var.set(f"{avg_len:.4f}")
        self.redundancy_var.set(f"{redundancy:.6f}")

        # Заполняем таблицу
        for sym, p in sorted(symbols_probs, key=lambda x: -x[1]):
            code = codes.get(sym, "")
            repr_sym = repr(sym)
            if sym == ' ':
                repr_sym = "[пробел]"
            elif sym == '\n':
                repr_sym = "[перевод]"
            self.tree.insert("", "end", values=(repr_sym, f"{p:.5f}", code))

# ---------- Запуск ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = InfoTheoryApp(root)

    root.mainloop()
