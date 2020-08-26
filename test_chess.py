from chess import *

board = Board()

pieces_decoder_dict = {
    'P': PAWN,
    'N': KNIGHT,
    'B': BISHOP,
    'Q': QUEEN,
    'K': KING,
    'R': ROOK
}

print(board)

# Moving pieces like this works
# Like this doesn't:
#   pawn = board1.get_piece(chess.locate("e2"))
#   board.move_piece(pawn, chess.locate("e4"))

board.move_piece(locate_piece(PAWN, WHITE, locate("a2")), locate("a3"))

print(board)

board.move_piece(locate_piece(BISHOP, WHITE, locate("b1")), locate("a2"))

print(board)

board.move_piece(locate_piece(KNIGHT, WHITE, locate("c1")), locate("b3"))

print(board)
print(board.in_check(WHITE))
print(list(board.get_moves(1)))  # Available moves. 0 or 1 indicates whites or blacks

print(board.get_piece(chess.locate("a2")))  # Should be a white bishop (wBa2)
print(board.get_piece(chess.locate("b3")))  # Should be a white Knight (wNb3)

# needs: board, movements_ahead, whites or blacks, stuff
# More than 3 movements ahead takes an eternity to compute
_, move = ai.minimax_with_pruning(board, 4, 1, alpha=-1000, beta=1000)
print(move)
_, move = ai.minimax(board, 3, 1)   # Looks kinda better
print(move)

parse = str(move).split(' to ')
end_pos = parse[1]
piece = pieces_decoder_dict[parse[0][1]]
start_pos = parse[0][-2:]

board.move_piece(locate_piece(piece, BLACK, locate(start_pos)), locate(end_pos))
print(board)
