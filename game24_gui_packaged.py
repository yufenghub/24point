import tkinter as tk
from tkinter import messagebox
import random, time, itertools, json, os, sys
from pathlib import Path

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_rank_path():
    appdata = os.getenv('APPDATA') or str(Path.home())
    save_dir = Path(appdata) / "My24Game"
    save_dir.mkdir(parents=True, exist_ok=True)
    rank_path = save_dir / "rank.json"
    if not rank_path.exists():
        tpl = resource_path("rank.json")
        try:
            import shutil
            shutil.copy(tpl, rank_path)
        except Exception:
            rank_path.write_text("[]", encoding="utf-8")
    return str(rank_path)

try:
    import winsound
    def play_sound(sound_type):
        if sound_type == "click":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sound_type == "correct":
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        elif sound_type == "wrong":
            winsound.MessageBeep(winsound.MB_ICONHAND)
except ImportError:
    try:
        import pygame
        pygame.mixer.init()
        def play_sound(sound_type):
            sounds = {
                "click": resource_path("click.wav"),
                "correct": resource_path("success.wav"),
                "wrong": resource_path("fail.wav"),
            }
            f = sounds.get(sound_type)
            if os.path.exists(f):
                pygame.mixer.Sound(f).play()
    except Exception:
        def play_sound(sound_type):
            pass

def can_make_24(nums):
    ops = ['+', '-', '*', '/']
    import itertools
    for ns in itertools.permutations(nums):
        for op1 in ops:
            for op2 in ops:
                for op3 in ops:
                    expressions = [
                        f"(({ns[0]}{op1}{ns[1]}){op2}{ns[2]}){op3}{ns[3]}",
                        f"({ns[0]}{op1}({ns[1]}{op2}{ns[2]})){op3}{ns[3]}",
                        f"{ns[0]}{op1}(({ns[1]}{op2}{ns[2]}){op3}{ns[3]})",
                        f"{ns[0]}{op1}({ns[1]}{op2}({ns[2]}{op3}{ns[3]}))",
                        f"({ns[0]}{op1}{ns[1]}){op2}({ns[2]}{op3}{ns[3]})"
                    ]
                    for expr in expressions:
                        try:
                            if abs(eval(expr) - 24) < 1e-6:
                                return True
                        except ZeroDivisionError:
                            continue
    return False

def validate_expression(expr, nums):
    allowed_ops = set('0123456789+-*/() ')
    if not set(expr).issubset(allowed_ops):
        return False
    used_nums = [int(x) for x in expr if x.isdigit()]
    temp_nums = nums.copy()
    for n in used_nums:
        if n in temp_nums:
            temp_nums.remove(n)
        else:
            return False
    return True

class Game24App:
    def __init__(self, root):
        self.root = root
        self.root.title("🃏 24点扑克牌游戏")
        self.root.geometry("540x520")
        self.root.config(bg="#F3F4F6")
        self.root.resizable(False, False)
        self.player_name = ""
        self.round = 0
        self.total_score = 0
        self.time_limit = 20
        self.start_time = None
        self.nums = []
        self.timer_running = False
        self.build_start_screen()

    def styled_button(self, text, command):
        return tk.Button(self.root, text=text, command=lambda: [play_sound("click"), command()],
                         bg="#4F46E5", fg="white", activebackground="#6366F1",
                         font=("Helvetica", 12, "bold"), relief="flat",
                         bd=0, padx=10, pady=6, cursor="hand2")

    def build_start_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        tk.Label(self.root, text="🃏 24点扑克牌游戏", font=("Helvetica", 26, "bold"),
                 bg="#F3F4F6", fg="#111827").pack(pady=40)
        tk.Label(self.root, text="请输入玩家姓名：", font=("Helvetica", 13),
                 bg="#F3F4F6").pack()
        self.name_entry = tk.Entry(self.root, font=("Helvetica", 14),
                                   relief="solid", bd=1, width=18)
        self.name_entry.pack(pady=12)
        self.styled_button("开始游戏", self.start_game).pack(pady=8)
        self.styled_button("查看排行榜", self.show_rank).pack(pady=8)
        self.styled_button("退出游戏", self.root.quit).pack(pady=8)

    def flash_cards(self, cards):
        def animate(i=0):
            if i >= 6: return
            color = "#FBBF24" if i % 2 == 0 else "#3B82F6"
            for card in cards:
                card.config(bg=color)
            self.root.after(150, animate, i+1)
        animate()

    def start_game(self):
        self.player_name = self.name_entry.get().strip()
        if not self.player_name:
            messagebox.showwarning("提示", "请输入玩家姓名！")
            return
        self.round = 0
        self.total_score = 0
        self.next_round()

    def next_round(self):
        self.round += 1
        if self.round > 3:
            self.end_game()
            return
        for w in self.root.winfo_children():
            w.destroy()
        self.nums = [random.randint(1, 10) for _ in range(4)]
        self.start_time = time.time()
        self.timer_running = True
        tk.Label(self.root, text=f"第 {self.round} 轮", font=("Helvetica", 16, "bold"),
                 bg="#F3F4F6", fg="#1E3A8A").pack(pady=10)
        card_frame = tk.Frame(self.root, bg="#F3F4F6")
        card_frame.pack(pady=20)
        cards = []
        for n in self.nums:
            card = tk.Label(card_frame, text=str(n), width=4, height=2,
                            font=("Helvetica", 22, "bold"), fg="#1E3A8A",
                            bg=random.choice(["#E0F2FE", "#FEE2E2", "#DCFCE7", "#FEF3C7"]),
                            relief="raised", bd=4)
            card.pack(side="left", padx=10)
            cards.append(card)
        self.flash_cards(cards)
        tk.Label(self.root, text=f"请输入表达式或 NO（限时 {self.time_limit} 秒）",
                 font=("Helvetica", 12), bg="#F3F4F6").pack()
        self.expr_entry = tk.Entry(self.root, font=("Helvetica", 14),
                                   relief="solid", bd=1, width=22)
        self.expr_entry.pack(pady=10)
        self.styled_button("提交答案", self.submit_answer).pack(pady=8)
        self.time_label = tk.Label(self.root, text=f"剩余时间：{self.time_limit} 秒",
                                   font=("Helvetica", 12), bg="#F3F4F6", fg="#DC2626")
        self.time_label.pack(pady=5)
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        elapsed = time.time() - self.start_time
        remaining = int(self.time_limit - elapsed)
        if remaining <= 0:
            self.timer_running = False
            play_sound("wrong")
            messagebox.showinfo("超时", "时间到！本轮得分为 0。")
            self.next_round()
            return
        self.time_label.config(text=f"剩余时间：{remaining} 秒")
        self.root.after(1000, self.update_timer)

    def submit_answer(self):
        if not self.timer_running:
            return
        self.timer_running = False
        expr = self.expr_entry.get().strip()
        elapsed = time.time() - self.start_time
        if expr.upper() == "NO":
            correct = not can_make_24(self.nums)
            if correct:
                self.total_score += 10
                play_sound("correct")
                messagebox.showinfo("正确", f"判断正确！+10 分\n当前总分：{self.total_score}")
            else:
                play_sound("wrong")
                messagebox.showinfo("错误", "判断错误！本轮得 0 分。")
            self.next_round()
            return
        if not validate_expression(expr, self.nums):
            play_sound("wrong")
            messagebox.showwarning("非法输入", "表达式非法或未正确使用数字！")
            self.next_round()
            return
        try:
            result = eval(expr)
        except Exception:
            play_sound("wrong")
            messagebox.showwarning("错误", "表达式计算错误！")
            self.next_round()
            return
        if abs(result - 24) < 1e-6:
            score = max(0, int(30 - elapsed))
            self.total_score += score
            play_sound("correct")
            messagebox.showinfo("正确", f"恭喜答对！用时 {elapsed:.1f}s，得 {score} 分。")
        else:
            play_sound("wrong")
            messagebox.showinfo("错误", f"结果为 {result}，不是 24。得 0 分。")
        self.next_round()

    def end_game(self):
        self.save_score()
        play_sound("click")
        messagebox.showinfo("游戏结束", f"{self.player_name} 的总分为 {self.total_score}")
        self.build_start_screen()

    def save_score(self):
        rank_file = get_rank_path()
        try:
            data = json.load(open(rank_file, "r", encoding="utf-8"))
        except Exception:
            data = []
        data.append({"name": self.player_name, "score": self.total_score})
        data = sorted(data, key=lambda x: x["score"], reverse=True)[:10]
        with open(rank_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def show_rank(self):
        rank_file = get_rank_path()
        try:
            data = json.load(open(rank_file, "r", encoding="utf-8"))
        except Exception:
            messagebox.showinfo("排行榜", "暂无记录")
            return
        rank_text = "🏆 排行榜前十名：\n\n"
        for i, item in enumerate(data, 1):
            rank_text += f"{i}. {item['name']} - {item['score']} 分\n"
        play_sound("click")
        messagebox.showinfo("排行榜", rank_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = Game24App(root)
    root.mainloop()

