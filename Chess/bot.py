import random
from figures import Color
from board import Board, opposite_color


class Bot:
    def __init__(self, level='easy'):
        self.level = level

    def get_move(self, board: Board, color: Color):
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = board.squares[row][col]
                if piece and piece.color == color:
                    moves = board.get_valid_moves(piece.pos)
                    if moves:
                        pieces.append((piece, moves))

        if not pieces:
            return None

        if self.level == 'easy':
            # Случайный ход
            p, moves = random.choice(pieces)
            return p, random.choice(moves)

        elif self.level == 'medium':
            # Приоритет: шах > взятие > развитие
            best_moves = []
            for p, moves in pieces:
                for move in moves:
                    # Проверяем, не поставит ли ход шаг самому себе (уже проверено в get_valid_moves)
                    # Приоритет 3: шах
                    board_copy = board.copy()
                    board_copy.move_piece(p.pos, move)
                    if board_copy.is_in_check(opposite_color(color)):
                        return p, move  # Шах - лучший ход

                    # Приоритет 2: взятие
                    target = board.get_piece(move)
                    if target:
                        best_moves.append((p, move, 2))
                    else:
                        # Приоритет 1: обычный ход
                        best_moves.append((p, move, 1))

            if best_moves:
                best_moves.sort(key=lambda x: x[2], reverse=True)
                return best_moves[0][0], best_moves[0][1]

        # Если ничего не нашли
        return pieces[0][0], random.choice(pieces[0][1])