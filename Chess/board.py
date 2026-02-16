from figures import *
import copy


class Board:
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.squares[0][1] = Knight("b8", Color.BLACK)
        self.squares[0][4] = King("e8", Color.BLACK)
        self.squares[1][4] = Pawn("e7", Color.BLACK)
        self.squares[7][2] = Bishop("c1", Color.WHITE)
        self.squares[7][4] = King("e1", Color.WHITE)
        self.squares[7][5] = Bishop("f1", Color.WHITE)

    def get(self, pos):
        r, c = pos_to_coord(pos)
        return self.squares[r][c] if 0 <= r < 8 and 0 <= c < 8 else None

    def all_pieces(self, color):
        return [self.squares[r][c] for r in range(8) for c in range(8) if
                self.squares[r][c] and self.squares[r][c].color == color]

    def attacked(self, color):
        att = []
        for r in range(8):
            for c in range(8):
                p = self.squares[r][c]
                if p and p.color == color:
                    if isinstance(p, Knight):
                        for rr in range(8):
                            for cc in range(8):
                                t = coord_to_pos(rr, cc)
                                if p.can_move(t): att.append(t)
                    else:
                        dirs = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
                        for dr, dc in dirs:
                            rr, cc = r + dr, c + dc
                            while 0 <= rr < 8 and 0 <= cc < 8:
                                t = coord_to_pos(rr, cc)
                                if not p.can_move(t): break
                                att.append(t)
                                if self.squares[rr][cc]: break
                                rr += dr
                                cc += dc
        return list(set(att))

    def _get_sliding_moves(self, piece):
        dirs = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        r, c = pos_to_coord(piece.pos)
        moves = []

        for dr, dc in dirs:
            rr, cc = r + dr, c + dc
            while 0 <= rr < 8 and 0 <= cc < 8:
                t = coord_to_pos(rr, cc)
                if not piece.can_move(t): break
                tp = self.squares[rr][cc]

                # Особая логика для пешки
                if isinstance(piece, Pawn):
                    dx = ord(t[0]) - ord(piece.pos[0])
                    dy = int(t[1]) - int(piece.pos[1])

                    if piece.color == Color.WHITE:
                        # Взятие по диагонали
                        if abs(dx) == 1 and dy == 1:
                            if not tp or tp.color == piece.color:
                                break
                        # Ход прямо
                        elif dx == 0:
                            if dy == 1:
                                if tp: break
                            elif dy == 2:
                                if piece.pos[1] != '2' or tp or self.get(piece.pos[0] + '3'):
                                    break
                            else:
                                break
                        else:
                            break
                    else:  # BLACK
                        # Взятие по диагонали
                        if abs(dx) == 1 and dy == -1:
                            if not tp or tp.color == piece.color:
                                break
                        # Ход прямо
                        elif dx == 0:
                            if dy == -1:
                                if tp: break
                            elif dy == -2:
                                if piece.pos[1] != '7' or tp or self.get(piece.pos[0] + '6'):
                                    break
                            else:
                                break
                        else:
                            break

                if tp:
                    if tp.color != piece.color and not isinstance(tp, King):
                        moves.append(t)
                    break
                else:
                    moves.append(t)

                if isinstance(piece, Pawn) and abs(rr - r) == 2:
                    break

                rr += dr
                cc += dc
        return moves

    def valid_moves(self, pos):
        p = self.get(pos)
        if not p: return []

        if isinstance(p, Knight):
            raw = []
            for r in range(8):
                for c in range(8):
                    t = coord_to_pos(r, c)
                    if p.can_move(t):
                        tp = self.get(t)
                        if not tp or tp.color != p.color:
                            raw.append(t)
        else:
            raw = self._get_sliding_moves(p)

        legal = []
        for m in raw:
            b2 = self.copy()
            if b2._force(p.pos, m) and not b2.in_check(p.color):
                legal.append(m)
        return legal

    def _force(self, frm, to):
        fr, fc = pos_to_coord(frm)
        tr, tc = pos_to_coord(to)
        p = self.squares[fr][fc]
        if not p or (self.squares[tr][tc] and isinstance(self.squares[tr][tc], King)):
            return False
        self.squares[tr][tc] = p
        self.squares[fr][fc] = None
        p.pos = to
        return True

    def move(self, frm, to):
        p = self.get(frm)
        if not p or to not in self.valid_moves(frm):
            return False

        fr, fc = pos_to_coord(frm)
        tr, tc = pos_to_coord(to)

        # Нельзя съесть короля
        if self.squares[tr][tc] and isinstance(self.squares[tr][tc], King):
            return False

        # Взятие на проходе
        if isinstance(p, Pawn) and abs(ord(to[0]) - ord(frm[0])) == 1 and not self.get(to):
            self.squares[fr][tc] = None

        # Превращение пешки
        if isinstance(p, Pawn) and p.can_promote(to):
            self.squares[tr][tc] = Queen(to, p.color)
            self.squares[fr][fc] = None
            return True

        # Обычный ход
        self.squares[tr][tc] = p
        self.squares[fr][fc] = None
        p.pos = to
        return True

    def in_check(self, color):
        k = self.king_pos(color)
        return k in self.attacked(opposite_color(color)) if k else False

    def checkmate(self, color):
        if not self.in_check(color):
            return False
        for p in self.all_pieces(color):
            if self.valid_moves(p.pos):
                return False
        return True

    def stalemate(self, color):
        if self.in_check(color):
            return False
        for p in self.all_pieces(color):
            if self.valid_moves(p.pos):
                return False
        return True

    def king_pos(self, color):
        for r in range(8):
            for c in range(8):
                p = self.squares[r][c]
                if p and isinstance(p, King) and p.color == color:
                    return coord_to_pos(r, c)
        return None

    def copy(self):
        b = Board()
        for r in range(8):
            for c in range(8):
                b.squares[r][c] = None

        for r in range(8):
            for c in range(8):
                p = self.squares[r][c]
                if p:
                    cls = p.__class__
                    new = cls(p.pos, p.color)
                    # Копируем специфические атрибуты
                    if isinstance(new, Pawn):
                        new.jump = p.jump
                    b.squares[r][c] = new
        return b


def pos_to_coord(p):
    return 8 - int(p[1]), ord(p[0]) - ord('a')


def coord_to_pos(r, c):
    return chr(ord('a') + c) + str(8 - r)


def opposite_color(c):
    return Color.BLACK if c == Color.WHITE else Color.WHITE