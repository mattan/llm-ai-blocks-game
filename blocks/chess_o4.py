import pygame
import chess
import sys

# הגדרות
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE = (232, 235, 239)
GRAY = (125, 135, 150)
BLUE = (106, 156, 227)
GREEN = (120, 200, 120)
FONT_NAME = 'Segoe UI Symbol'
PIECE_UNICODES = {
    chess.PAWN:   ('♙', '♟'),
    chess.KNIGHT: ('♘', '♞'),
    chess.BISHOP: ('♗', '♝'),
    chess.ROOK:   ('♖', '♜'),
    chess.QUEEN:  ('♕', '♛'),
    chess.KING:   ('♔', '♚'),
}

def draw_board(win, board, selected=None, legal_moves=[]):
    win.fill(WHITE)
    font = pygame.font.SysFont(FONT_NAME, SQUARE_SIZE//2)
    for row in range(ROWS):
        for col in range(COLS):
            color = GRAY if (row+col)%2 else WHITE
            rect = pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(win, color, rect)
            if selected == (row, col):
                pygame.draw.rect(win, BLUE, rect, 4)
            elif (row, col) in legal_moves:
                pygame.draw.rect(win, GREEN, rect, 4)
            # מציג כלי
            sq = chess.square(col, 7-row)  # התאמת שורת ה־pygame לשחמט
            p = board.piece_at(sq)
            if p:
                symbol = PIECE_UNICODES[p.piece_type][0 if p.color==chess.WHITE else 1]
                text = font.render(symbol, True, (20,20,20))
                text_rect = text.get_rect(center=rect.center)
                win.blit(text, text_rect)
    pygame.display.update()

def get_board_pos(mouse):
    x, y = mouse
    col = x // SQUARE_SIZE
    row = y // SQUARE_SIZE
    if 0<=col<8 and 0<=row<8:
        return (row, col)
    return None

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Professional Chess (with python-chess)")
    board = chess.Board()
    selected = None
    legal_moves = []
    running = True
    game_over = False

    promotion_move = None
    promotion_surf = None
    promotion_rects = []
    font = pygame.font.SysFont(FONT_NAME, SQUARE_SIZE//3)

    while running:
        draw_board(win, board, selected, legal_moves)

        if board.is_checkmate():
            game_over = True
        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            game_over = True

        if game_over:
            msg = "Checkmate!" if board.is_checkmate() else "Draw!"
            color = (220,60,60) if board.is_checkmate() else (60,60,220)
            sfont = pygame.font.SysFont(FONT_NAME, 40)
            label = sfont.render(msg, True, color)
            win.blit(label, (WIDTH//2-label.get_width()//2, HEIGHT//2-label.get_height()//2))
            pygame.display.update()
            pygame.time.wait(4000)
            running = False
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not promotion_move:
                pos = get_board_pos(event.pos)
                if pos:
                    row, col = pos
                    sq = chess.square(col, 7-row)
                    if selected is None:
                        p = board.piece_at(sq)
                        if p and p.color == board.turn:
                            selected = (row, col)
                            # רק המהלכים החוקיים לכלי הזה
                            legal_moves = []
                            for mv in board.legal_moves:
                                if mv.from_square == sq:
                                    legal_moves.append((7-chess.square_rank(mv.to_square), chess.square_file(mv.to_square)))
                        else:
                            selected = None
                            legal_moves = []
                    else:
                        s_row, s_col = selected
                        from_sq = chess.square(s_col, 7-s_row)
                        to_sq = chess.square(col, 7-row)
                        move = chess.Move(from_sq, to_sq)
                        # קידום חייל
                        if chess.PAWN == board.piece_type_at(from_sq) and ((board.turn == chess.WHITE and (7-row)==7) or (board.turn == chess.BLACK and (7-row)==0)):
                            promotion_pieces = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
                            promotion_move = (from_sq, to_sq)
                            # שרטוט אפשרויות קידום
                            promotion_surf = pygame.Surface((4*SQUARE_SIZE, SQUARE_SIZE))
                            promotion_surf.fill((240,240,180))
                            promotion_rects = []
                            for i, pc in enumerate(promotion_pieces):
                                symbol = PIECE_UNICODES[pc][0 if board.turn==chess.WHITE else 1]
                                txt = font.render(symbol, True, (20,20,20))
                                rect = pygame.Rect(i*SQUARE_SIZE, 0, SQUARE_SIZE, SQUARE_SIZE)
                                promotion_surf.blit(txt, txt.get_rect(center=rect.center))
                                promotion_rects.append(rect)
                            px = col*SQUARE_SIZE
                            py = row * SQUARE_SIZE
                            win.blit(promotion_surf, (px, py))
                            pygame.display.update()
                            continue
                        # מהלך רגיל
                        if move in board.legal_moves:
                            board.push(move)
                        selected = None
                        legal_moves = []

            elif event.type == pygame.MOUSEBUTTONDOWN and promotion_move:
                mx, my = event.pos
                f_sq, t_sq = promotion_move
                pr, pc = (7-chess.square_rank(t_sq), chess.square_file(t_sq))
                px = pc*SQUARE_SIZE
                py = pr*SQUARE_SIZE
                rel = (mx-px, my-py)
                # מתוך 4 אפשרויות קידום
                promo = None
                for i, piece in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
                    r = pygame.Rect(i*SQUARE_SIZE, 0, SQUARE_SIZE, SQUARE_SIZE)
                    if r.collidepoint(rel):
                        promo = piece
                        break
                if promo:
                    move = chess.Move(f_sq, t_sq, promotion=promo)
                    if move in board.legal_moves:
                        board.push(move)
                selected = None
                legal_moves = []
                promotion_move = None

        pygame.time.delay(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
