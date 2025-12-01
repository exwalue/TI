import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===

def build_cumulative_probabilities(freq_dict):
    """Строит кумулятивные вероятности + упорядоченный список символов"""
    total = sum(freq_dict.values())
    cum = 0.0
    symbols = sorted(freq_dict.keys())
    cum_dict = {}
    prob_dict = {}

    for symbol in symbols:
        prob = freq_dict[symbol] / total
        prob_dict[symbol] = prob
        cum_dict[symbol] = (cum, cum + prob)
        cum += prob

    return cum_dict, symbols, prob_dict


def encode_arithmetic(message_with_eof, cum_dict, symbols):
    low, high = 0.0, 1.0
    steps = [(0, "", f"[{low:.10f}; {high:.10f})")]
    current = ""

    for i, symbol in enumerate(message_with_eof, 1):
        s_low, s_high = cum_dict[symbol]
        interval = high - low

        new_low = low + interval * s_low
        new_high = low + interval * s_high

        low, high = new_low, new_high

        current += symbol if symbol != '\x04' else '␄'
        steps.append((i, current, f"[{low:.10f}; {high:.10f})"))

    return low, steps



def decode_arithmetic(code, cum_dict, symbols, max_len=1000):
    low, high = 0.0, 1.0
    decoded = ""
    steps = [(0, "", f"[{low:.10f}; {high:.10f})")]

    for step in range(1, max_len + 1):
        interval = high - low
        found = False

        for symbol in symbols:
            s_low, s_high = cum_dict[symbol]
            symbol_low = low + interval * s_low
            symbol_high = low + interval * s_high

            if symbol_low <= code < symbol_high:
                low, high = symbol_low, symbol_high
                decoded += symbol
                disp = decoded.replace('\x04', '␄')
                steps.append((step, disp, f"[{low:.10f}; {high:.10f})"))

                if symbol == '\x04':
                    return decoded[:-1], steps

                found = True
                break

        if not found:
            raise ValueError("Ошибка: код не попадает в интервалы")

    raise ValueError("Превышена максимальная длина декодирования")


# === GUI ===

class ArithmeticCoderApp:
    def __init__(self, root):
        self.root = root
        root.title("Арифметическое кодирование")
        root.geometry("1100x720")
        root.resizable(True, True)

        self.original_text = ""

        # Ввод текста
        tk.Label(root, text="Введите текст для кодирования:").pack(pady=(10, 0))
        self.text_input = tk.Text(root, height=3)
        self.text_input.pack(padx=10, pady=5, fill=tk.X)

        # Кнопки
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Кодировать", command=self.encode).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Декодировать", command=self.decode).pack(side=tk.LEFT, padx=5)

        # Результат кодирования
        tk.Label(root, text="Результат кодирования:").pack(pady=(10, 0))
        self.result_text = tk.Entry(root, font=("Courier", 10), state='readonly')
        self.result_text.pack(padx=10, fill=tk.X)

        # Результат декодирования
        tk.Label(root, text="Результат декодирования:").pack(pady=(10, 0))
        self.decoded_text = tk.Entry(root, font=("Courier", 10), state='readonly')
        self.decoded_text.pack(padx=10, fill=tk.X)

        # === Таблица вероятностей ===
        tk.Label(root, text="Таблица вероятностей символов:").pack(pady=(10, 0))
        prob_frame = tk.Frame(root)
        prob_frame.pack(padx=10, pady=5, fill=tk.X)

        columns = ("Символ", "Частота", "P", "Low", "High")
        self.prob_tree = ttk.Treeview(prob_frame, columns=columns, show="headings", height=6)

        for col in columns:
            self.prob_tree.heading(col, text=col)
            self.prob_tree.column(col, width=120)

        self.prob_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # === Таблица шагов ===
        tk.Label(root, text="Этапы кодирования/декодирования:").pack(pady=(10, 0))
        tree_frame = tk.Frame(root)
        tree_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        columns = ("Шаг", "Цепочка", "Интервал")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_prob_table(self):
        for item in self.prob_tree.get_children():
            self.prob_tree.delete(item)

    def encode(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Ошибка", "Введите текст!")
            return

        self.original_text = raw_text
        message = raw_text + '\x04'

        freq = Counter(message)
        cum_dict, symbols, prob_dict = build_cumulative_probabilities(freq)

        # Заполняем таблицу вероятностей
        self.clear_prob_table()
        for s in symbols:
            ch = s if s != '\x04' else "␄"
            low, high = cum_dict[s]
            self.prob_tree.insert("", tk.END,
                                  values=(ch, freq[s], f"{prob_dict[s]:.5f}",
                                          f"{low:.5f}", f"{high:.5f}"))

        try:
            final_low, steps = encode_arithmetic(message, cum_dict, symbols)

            self.clear_tree()
            for step in steps:
                self.tree.insert("", tk.END, values=step)

            self.result_text.config(state='normal')
            self.result_text.delete(0, tk.END)
            self.result_text.insert(0, f"{final_low:.12f}")
            self.result_text.config(state='readonly')

        except Exception as e:
            messagebox.showerror("Ошибка кодирования", str(e))

    def decode(self):
        code_str = self.result_text.get()
        if not code_str:
            messagebox.showwarning("Ошибка", "Нет закодированного значения!")
            return

        try:
            code = float(code_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный код!")
            return

        if not self.original_text:
            messagebox.showwarning("Ошибка", "Нет исходного текста!")
            return

        message = self.original_text + '\x04'
        freq = Counter(message)
        cum_dict, symbols, _ = build_cumulative_probabilities(freq)

        try:
            decoded, steps = decode_arithmetic(code, cum_dict, symbols)

            self.clear_tree()
            for step in steps:
                self.tree.insert("", tk.END, values=step)

            self.decoded_text.config(state='normal')
            self.decoded_text.delete(0, tk.END)
            self.decoded_text.insert(0, decoded)
            self.decoded_text.config(state='readonly')

        except Exception as e:
            messagebox.showerror("Ошибка декодирования", str(e))


# === ЗАПУСК ===
if __name__ == "__main__":
    root = tk.Tk()
    app = ArithmeticCoderApp(root)
    root.mainloop()
