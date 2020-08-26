import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import glob
from chess import *

pygame.init()
pygame.font.init()
pygame.display.set_caption('Diego Bonilla Chess Cutre')

myfont = pygame.font.Font('./data/Sketch Gothic School.ttf', 200)
check_good = myfont.render('CHECK', False, (0, 255, 0))
check_bad = myfont.render('CHECK', False, (255, 0, 0))
check_mate = myfont.render('CHECK MATE', False, (0, 0, 0))

WIDTH, HEIGHT = 1000, 1000
CELL_SIZE = 110
PIECE_WIDTH, PIECE_HEIGHT = CELL_SIZE, CELL_SIZE
BOARD_BORDER = 60
screen = pygame.display.set_mode([WIDTH, HEIGHT])
clock = pygame.time.Clock()

pieces_decoder_dict = {
    'P': PAWN,
    'N': KNIGHT,
    'B': BISHOP,
    'Q': QUEEN,
    'K': KING,
    'R': ROOK
}
pieces_encoder_dict = {
    PAWN: 'P',
    KNIGHT: 'N',
    BISHOP: 'B',
    QUEEN: 'Q',
    KING: 'K',
    ROOK: 'R'
}

board_image = pygame.image.load('./sprites/board.jpg')
board_image = pygame.transform.scale(board_image, (WIDTH, HEIGHT))
cell_indicator = pygame.Surface((CELL_SIZE, CELL_SIZE))
cell_indicator.set_alpha(128)
cell_indicator.fill((200, 30, 200))

pieces = glob.glob('./sprites/*.png')
white_pieces_dict = {}
black_pieces_dict = {}
for piece in pieces:
    name = os.path.split(piece)[-1][:-4]
    if name.startswith('w'):
        white_pieces_dict[name[-1]] = pygame.transform.scale(pygame.image.load(piece).convert_alpha(),
                                                             (PIECE_WIDTH, PIECE_HEIGHT))
    else:
        black_pieces_dict[name[-1]] = pygame.transform.scale(pygame.image.load(piece).convert_alpha(),
                                                             (PIECE_WIDTH, PIECE_HEIGHT))

board = Board()
previous_board = board.copy()

start_moving = False
start_pos = None
focus_piece = None
focus_piece_name = None
available_moves = None
last = None

difficulty = {
    'easy': 1,
    'normal': 2,
    'hard': 3
}

turn = 0

print("\'R\' for RESTART. \'Q / ESC\' for QUIT.")

running = True
while running:
    screen.blit(board_image, (0, 0))

    if turn == 1 and pygame.time.get_ticks() - last > 300:
        _, move = ai.minimax(board, difficulty['hard'], 1)
        parse = str(move).split(' to ')
        end_pos = parse[1]
        piece = pieces_decoder_dict[parse[0][1]]
        start_pos = parse[0][-2:]
        board.move_piece(locate_piece(piece, BLACK, locate(start_pos)), locate(end_pos))
        turn = 0

    is_white_king = False
    is_black_king = False
    for row_idx, row in enumerate(reversed(board.board)):
        for col_idx, col in enumerate(reversed(row)):
            x = y = (BOARD_BORDER + col_idx * CELL_SIZE, BOARD_BORDER + row_idx * CELL_SIZE)
            if start_moving:
                for move in available_moves:
                    if move.endswith(chr(97 + 7 - col_idx) + str(8 - row_idx)):
                        screen.blit(cell_indicator, (x, y))
            if col is None:
                continue
            col = str(col)
            if col.startswith('w'):
                is_white_king = col[1] == 'K' or is_white_king
                if start_moving and 7 - col_idx == focus_piece[0] and 7 - row_idx == focus_piece[1]:
                    x, y = pygame.mouse.get_pos()
                    x = x - CELL_SIZE // 2
                    y = y - CELL_SIZE // 2
                screen.blit(white_pieces_dict[col[1]], (x, y))
            else:
                is_black_king = col[1] == 'K' or is_black_king
                screen.blit(black_pieces_dict[col[1]], (x, y))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if turn:
                break
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if BOARD_BORDER > mouse_x or mouse_x > WIDTH - BOARD_BORDER:
                break
            if BOARD_BORDER > mouse_y or mouse_y > HEIGHT - BOARD_BORDER:
                break
            board_pos_x = 7 - int((mouse_x - BOARD_BORDER) / CELL_SIZE)
            board_pos_y = 8 - int((mouse_y - BOARD_BORDER) / CELL_SIZE)
            cell_name = chr(97 + board_pos_x) + str(board_pos_y)

            piece = board.get_piece(chess.locate(cell_name))
            if piece is None or str(piece).startswith('b'):
                break

            start_moving = True
            focus_piece = (board_pos_x, board_pos_y - 1)
            start_pos = cell_name
            focus_piece_name = pieces_decoder_dict[str(piece)[1]]
            available_moves = [str(move[0]) for move in list(board.get_moves(0))
                               if str(move[0]).startswith('w' + pieces_encoder_dict[focus_piece_name] + cell_name)]

        if event.type == pygame.MOUSEBUTTONUP:
            if turn:
                break
            if not start_moving:
                break
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if BOARD_BORDER > mouse_x or mouse_x > WIDTH - BOARD_BORDER:
                start_moving = False
                focus_piece = None
                break
            if BOARD_BORDER > mouse_y or mouse_y > HEIGHT - BOARD_BORDER:
                start_moving = False
                focus_piece = None
                break

            board_pos_x = 7 - int((mouse_x - BOARD_BORDER) / CELL_SIZE)
            board_pos_y = 8 - int((mouse_y - BOARD_BORDER) / CELL_SIZE)
            cell_name = chr(97 + board_pos_x) + str(board_pos_y)

            if start_pos == cell_name:
                start_moving = False
                break

            if not any([move.endswith(cell_name) for move in available_moves]):
                start_moving = False
                break

            previous_board = board.copy()

            board.move_piece(locate_piece(focus_piece_name, WHITE, locate(start_pos)), locate(cell_name))

            available_moves = None
            start_pos = None
            start_moving = False
            focus_piece = None
            focus_piece_name = None
            last = pygame.time.get_ticks()
            turn = 1

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                running = False
            if event.key == pygame.K_r:
                board = previous_board
        if event.type == pygame.QUIT:
            running = False

    msg = None
    if board.in_check(WHITE):
        msg = check_bad
    if board.in_check(BLACK):
        msg = check_good
    if msg is not None:
        screen.blit(msg, (WIDTH // 2 - msg.get_rect().size[0] // 2, HEIGHT // 2 - msg.get_rect().size[1] // 2))
    if not is_black_king:
        print("YOU WIN")
        print("Points:", board.compute_score(0))
        running = False
    elif not is_white_king:
        print("YOU LOOSE")
        print("Points:", board.compute_score(0))
        running = False

    pygame.display.update()
    clock.tick(30)

pygame.quit()
