import pygame, tkinter as tk, os, time, random
from tkinter import ttk, messagebox
from cryptography.fernet import Fernet
from figures import Color
from board import Board, pos_to_coord, coord_to_pos, opposite_color
import items as ci

W, H, CELL = 800, 600, 75
COLORS = {'bg': (0, 0, 0), 'light': (173, 170, 166), 'dark': (124, 115, 115), 'yellow': (255, 255, 0),
          'white': (255, 255, 255), 'red': (199, 0, 0), 'green': (0, 255, 0), 'brown': (210, 180, 140)}


class Auth:
    def __init__(self):
        self.cipher = Fernet(
            Fernet.generate_key() if not os.path.exists("secret.key") else open("secret.key", "rb").read())
        if not os.path.exists("secret.key"): open("secret.key", "wb").write(self.cipher._encryption_key)

    def register(self, u, p):
        with open("credentials.txt", "a") as f: f.write(f"{u}:{self.cipher.encrypt(p.encode()).decode()}\n")

    def login(self, u, p):
        try:
            with open("credentials.txt", "r") as f:
                for l in f:
                    uu, pp = l.strip().split(":")
                    if uu == u and self.cipher.decrypt(pp.encode()).decode() == p: return True
        except:
            pass
        return False


def show_login():
    auth, root = Auth(), tk.Tk()
    root.title("Шахматы - Вход");
    root.geometry("500x500");
    root.configure(bg='#2c3e50');
    root.resizable(False, False)
    status = [False]
    tk.Label(root, text="ШАХМАТЫ", font=('Arial', 24, 'bold'), fg='#e74c3c', bg='#2c3e50').pack(pady=20)
    nb = ttk.Notebook(root);
    nb.pack(expand=1, fill="both", padx=20, pady=10)

    rf = ttk.Frame(nb);
    nb.add(rf, text="Регистрация")
    tk.Label(rf, text="Имя:").pack(pady=5);
    ru = tk.Entry(rf);
    ru.pack(pady=5)
    tk.Label(rf, text="Пароль:").pack(pady=5);
    rp = tk.Entry(rf, show="*");
    rp.pack(pady=5)

    def reg():
        if ru.get() and rp.get():
            auth.register(ru.get(), rp.get()); messagebox.showinfo("Успех", "Регистрация успешна!"); ru.delete(0,
                                                                                                               tk.END); rp.delete(
                0, tk.END)
        else:
            messagebox.showwarning("Ошибка", "Заполните поля")

    ttk.Button(rf, text="Зарегистрироваться", command=reg).pack(pady=20)

    lf = ttk.Frame(nb);
    nb.add(lf, text="Вход")
    tk.Label(lf, text="Имя:").pack(pady=5);
    lu = tk.Entry(lf);
    lu.pack(pady=5)
    tk.Label(lf, text="Пароль:").pack(pady=5);
    lp = tk.Entry(lf, show="*");
    lp.pack(pady=5)

    def log():
        if auth.login(lu.get(), lp.get()):
            status[0] = True; root.destroy()
        else:
            messagebox.showerror("Ошибка", "Неверные данные")

    ttk.Button(lf, text="Войти", command=log).pack(pady=20)
    tk.Label(root, text="♔ ♕ ♖ ♗ ♘ ♙", font=('Arial', 16), fg='#7f8c8d', bg='#2c3e50').pack(pady=10)
    root.mainloop()
    return status[0]


class Clock:
    def __init__(self, m=5): self.t = {'white': m * 60,
                                       'black': m * 60}; self.c = 'white'; self.l = time.time(); self.r = False

    def start(self, p='white'): self.c = p; self.l = time.time(); self.r = True

    def switch(self): self.update(); self.c = 'black' if self.c == 'white' else 'white'

    def update(self):
        if self.r: e = time.time() - self.l; self.t[self.c] = max(0, self.t[self.c] - e); self.l = time.time()

    def get(self, c): m, s = int(self.t[c]) // 60, int(self.t[c]) % 60; return f"{m:02d}:{s:02d}"

    def winner(self): return 'black' if self.t['white'] <= 0 else 'white' if self.t['black'] <= 0 else None


class Bot:
    def __init__(self, l='easy'):
        self.l = l

    def move(self, b, c):
        ps = [(b.squares[r][col], b.valid_moves(b.squares[r][col].pos)) for r in range(8) for col in range(8)
              if b.squares[r][col] and b.squares[r][col].color == c and b.valid_moves(b.squares[r][col].pos)]
        if not ps: return None
        if self.l == 'easy': p, ms = random.choice(ps); return p, random.choice(ms)
        for p, ms in ps:
            for m in ms:
                if b.get(m): return p, m
        p, ms = random.choice(ps);
        return p, random.choice(ms)


def init():
    pygame.font.init()
    try:
        pygame.mixer.init()
    except:
        pass
    global SC, F
    SC = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Шахматы с ботом")
    F = {'n': pygame.font.SysFont("Tahoma", 24), 's': pygame.font.SysFont("Tahoma", 20),
         'b': pygame.font.SysFont("Verdana", 40)}


def draw(b, s):
    SC.fill(COLORS['bg']);
    SC.blit(ci.CHESS_BOARD, (0, 0))
    pygame.draw.rect(SC, COLORS['light'], (600, 0, 200, 200))
    pygame.draw.rect(SC, COLORS['dark'], (600, 200, 200, 5))
    for i, cl in enumerate(['black', 'white']):
        y = 220 + (70 if cl == 'white' else 0);
        act = (s['player'] == cl);
        fr = COLORS['yellow'] if act else COLORS['brown']
        pygame.draw.rect(SC, fr, (610, y, 180, 60), 3)
        pygame.draw.rect(SC, COLORS['light'], (612, y + 2, 176, 56))
        t = F['s'].render(f"{cl.capitalize()}: {s['clock'].get(cl)}", True, COLORS['red'] if act else COLORS['bg'])
        SC.blit(t, (620, y + 20))
    pygame.draw.rect(SC, COLORS['white'], (600, 360, 200, 80))
    pygame.draw.rect(SC, COLORS['bg'], (600, 360, 200, 80), 2)
    t = F['n'].render(f"Ход: {s['player'].upper()}", True, COLORS['bg'])
    SC.blit(t, t.get_rect(center=(700, 400)))
    if s['check'] and int(time.time() * 2) % 2 == 0: SC.blit(F['n'].render("ШАХ!", True, COLORS['red']), (650, 530))
    if s.get('game_over'):
        o = pygame.Surface((W, H), pygame.SRCALPHA);
        o.fill((0, 0, 0, 128));
        SC.blit(o, (0, 0))
        txt = F['b'].render(f"{s['winner'].upper()} ПОБЕДИЛИ!" if s.get('checkmate') else "ПАТ!", True,
                            COLORS['green'] if s.get('checkmate') else COLORS['dark'])
        SC.blit(txt, txt.get_rect(center=(W // 2, H // 2)))
    for r in range(8):
        for c in range(8):
            p = b.squares[r][c]
            if p:
                x, y = c * CELL, r * CELL
                if s['selected'] and p.pos == s['selected'].pos: pygame.draw.rect(SC, COLORS['yellow'],
                                                                                  (x, y, CELL, CELL), 3)
                SC.blit(p.img, (x, y))
    if s['moves'] and not s.get('game_over'):
        for m in s['moves']:
            rr, cc = pos_to_coord(m)
            pygame.draw.circle(SC, COLORS['dark'], (cc * CELL + 37, rr * CELL + 37), 10)
    pygame.display.update()


def game():
    init()
    b, cl, bot = Board(), Clock(), Bot('easy')
    s = {'player': 'white', 'selected': None, 'moves': [], 'clock': cl, 'check': False, 'game_over': False,
         'checkmate': False, 'winner': None}
    cl.start('white');
    run = True
    while run:
        cl.update()
        if w := cl.winner():
            o = pygame.Surface((W, H), pygame.SRCALPHA);
            o.fill((0, 0, 0, 200));
            SC.blit(o, (0, 0))
            r = pygame.Rect(0, 0, 500, 150);
            r.center = (W // 2, H // 2)
            pygame.draw.rect(SC, COLORS['white'], r);
            pygame.draw.rect(SC, COLORS['bg'], r, 3)
            t = F['b'].render(f"{w.upper()} ПОБЕДИЛИ!", True, COLORS['green']);
            SC.blit(t, t.get_rect(center=(W // 2, H // 2)))
            if ci.CAPTURE_SOUND: ci.CAPTURE_SOUND.play()
            pygame.display.update();
            time.sleep(3);
            break
        if not s['game_over']:
            cur = Color.WHITE if s['player'] == 'white' else Color.BLACK
            if b.checkmate(cur):
                s['game_over'] = True; s['checkmate'] = True; s['winner'] = 'black' if s['player'] == 'white' else 'white'
            elif b.stalemate(cur):
                s['game_over'] = True; s['checkmate'] = False; s['winner'] = None
        if s['game_over']: draw(b, s); pygame.time.wait(3000); break
        if s['player'] == 'black' and not s['game_over']:
            pygame.time.wait(500);
            m = bot.move(b, Color.BLACK)
            if m:
                p, t = m
                if b.move(p.pos, t):
                    if ci.MOVE_SOUND: ci.MOVE_SOUND.play()
                    cl.switch();
                    s['player'] = 'white'
            continue
        for e in pygame.event.get():
            if e.type == pygame.QUIT: run = False; break
            if e.type == pygame.MOUSEBUTTONDOWN and not s['game_over'] and s['player'] == 'white':
                x, y = pygame.mouse.get_pos()
                if x < 600:
                    col, row = x // CELL, y // CELL
                    if 0 <= row < 8 and 0 <= col < 8:
                        if not s['selected']:
                            p = b.squares[row][col]
                            if p and p.color == Color.WHITE: s['selected'] = p; s['moves'] = b.valid_moves(p.pos)
                        else:
                            t = coord_to_pos(row, col)
                            if t in s['moves'] and b.move(s['selected'].pos, t):
                                if ci.MOVE_SOUND: ci.MOVE_SOUND.play()
                                cl.switch();
                                s['player'] = 'black'
                            s['selected'] = None;
                            s['moves'] = []
        if not s['game_over']:
            cur = Color.WHITE if s['player'] == 'white' else Color.BLACK
            s['check'] = b.in_check(cur)
        draw(b, s)
    pygame.quit()


if __name__ == "__main__":
    if show_login(): game()