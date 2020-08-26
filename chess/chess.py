"""
Chess.py - Defines necessary classes and (etc)

Some important aspects:
    All pieces and positions are stored in one array.
    This will act as reusable objects. 


TODO:
switch BLACK vs WHITE to white = 0, black = 1. 
"""

# Import
import chess.utils as utils
import numpy as np
import json

from copy import copy

# Chess Piece Colors
WHITE = 0
BLACK = 1

# Ches Piece Enumeration
KING = 0
QUEEN = 1
ROOK = 2
BISHOP = 3
KNIGHT = 4
PAWN = 5


# Functions
def generate_all_pieces():
    """
    Generates all combinations of pieces and positions. These objects
    are meant to be reused and this function will only be called once.
    Once called, it will be stored as a static variable of the
    board class. 
    """
    # TODO: Some Pawns are useless. Optimize later.
    types = [King, Queen, Rook, Knight, Bishop, Pawn]
    pieces = np.empty((6, 2, 8, 8), dtype=Piece)
    for color in [BLACK, WHITE]:
        for t in range(6):
            for row in range(8):
                for col in range(8):
                    pieces[t][color][row][col] = types[t](color, Position(row, col))
    return pieces


def locate_piece(type, color, position):
    return all_pieces[type][color][position.row][position.col]


def locate(pos_str):
    """
    Gives the position object based on the string. In this program, all 
    positions are represented by an instance of the Position class.
    This function aims to ease the use of positions within this program.
    >>> locate("a1")
    a1
    >>> locate("a2")
    a2
    >>> locate("a3")
    a3
    >>> locate("e4")
    e4
    >>> locate("f8")
    f8
    >>> locate("g8")
    g8
    >>> locate("h8")
    h8
    """
    return Position("12345678".index(pos_str[1]), "abcdefgh".index(pos_str[0]))


def piece_is_blocked_straight(piece, position, board):
    """
    Returns True if the straight path of piece to position is blocked.
    It does not check for whether there is a piece at the final destination
    since a move may be a valid attack. In addition, if position is not a
    straight movement of the initial, then True is returned since the piece
    is "blocked"
    >>> board = Board()
    >>> pawn1 = board.get_piece(locate("a2"))
    >>> piece_is_blocked_straight(pawn1, locate("a4"), board)
    False
    >>> piece_is_blocked_straight(pawn1, locate("b2"), board)
    False
    >>> piece_is_blocked_straight(pawn1, locate("a7"), board)
    False
    >>> piece_is_blocked_straight(pawn1, locate("a8"), board)
    True
    """
    row_change = position.row - piece.position.row
    col_change = position.col - piece.position.col

    n = abs(row_change)
    m = abs(col_change)

    if n == 0 or m == 0:
        row_unit = 0 if n == 0 else row_change // n
        col_unit = 0 if m == 0 else col_change // m
        path_length = max(n, m)

        for i in range(1, path_length):
            if board.get_piece(piece.position + (row_unit * i, col_unit * i)):
                return True
        return False
    return True


def piece_is_blocked_diagonal(piece, position, board):
    """
    Returns True if the diagonal path of piece to position is blocked.
    It does not check for whether there is a piece at the final destination
    since a move may be a valid attack. In addition, if position is not a
    diagonal movement of the initial, then True is returned since the piece
    is "blocked"
    >>> board = Board(empty=True)
    >>> queen = Queen(WHITE, locate("d1"))
    >>> board.add_piece(queen)
    >>> board.add_piece(Pawn(BLACK, locate("h5")))
    >>> board.add_piece(Pawn(WHITE, locate("c2"))) # Set up board
    >>> piece_is_blocked_diagonal(queen, locate("d1"), board) # Not valid move
    True
    >>> piece_is_blocked_diagonal(queen, locate("e2"), board) # Valid move
    False
    >>> piece_is_blocked_diagonal(queen, locate("f3"), board) # Valid move
    False
    >>> piece_is_blocked_diagonal(queen, locate("h5"), board) # Valid (see above)
    False
    >>> piece_is_blocked_diagonal(queen, locate("c2"), board) # Valid (see above)
    False
    >>> piece_is_blocked_diagonal(queen, locate("a4"), board) # Not valid move
    True
    >>> piece_is_blocked_diagonal(queen, locate("h1"), board) # Wrong move
    True
    >>> piece_is_blocked_diagonal(queen, locate("a2"), board) # Wrong move
    True
    """
    row_change = position.row - piece.position.row
    col_change = position.col - piece.position.col

    n = abs(row_change)
    m = abs(col_change)

    if n == m and n != 0:
        row_unit = row_change // n
        col_unit = col_change // m

        for i in range(1, n):
            if board.get_piece(piece.position + (row_unit * i, col_unit * i)):
                return True
        return False
    return True


# Position class
class Position:
    def __init__(self, row, col):
        """ 
        Constructs a position with row and col members.
        >>> pos = Position(3, 2)
        >>> pos.row
        3
        >>> pos.col
        2
        """
        self.row = row
        self.col = col
    
    def __str__(self):
        """
        Returns the chess board representation of position.
        >>> print(Position(0, 0))
        a1
        >>> print(Position(3, 2))
        c4
        """
        return "abcdefgh"[self.col] + "12345678"[self.row]

    def __repr__(self):
        """
        Returns the chess board representation of position.
        >>> Position(0, 0)
        a1
        >>> Position(3, 2)
        c4
        """
        return str(self)

    def __add__(self, pair):
        """
        Returns the position translated by a pair indicating the
        change in row and change in column.
        >>> locate("a1") + (1, 1)
        b2
        >>> locate("c4") + (1, -1)
        b5
        """
        return Position(self.row + pair[0], self.col + pair[1])

    def __eq__(self, other):
        """
        Returns true if two position objects are equal.
        >>> locate("a1") == locate("a1")
        True
        >>> locate("c3") == locate("d5")
        False
        """
        return self.row == other.row and self.col == other.col

    def in_range(self):
        """
        Returns true if row and col are in range.
        >>> Position(1, 3).in_range()
        True
        >>> Position(8, 8).in_range()
        False
        """
        return 0 <= self.row < 8 and 0 <= self.col < 8


# Move class
class Move:
    def __init__(self, piece, position, ep=False, castle=False, promote=None):
        self.piece = piece
        self.position = position
        self.ep = ep
        self.castle = castle
        self.promote = promote

    def from_json(json):
        piece = Piece.from_json(json["piece"])
        position = Position(json["position"]["row"],
                json["position"]["col"])
        ep = json["ep"]
        castle = json["castle"]
        promote = json["promote"]
        return Move(piece, position, ep=ep, castle=castle, promote=promote)

    def __repr__(self):
        return repr(self.piece) + " to " + repr(self.position)

    def __eq__(self, other):
        return self.piece == other.piece and self.position == other.position

# Board class
class Board:
    # For testing purposes:
    debug = False

    def __init__(self, empty=False, json=None):
        """ 
        Constructs a board with pieces in initial position.
        If empty is True, then board will not have any pieces.

        There are some instance variables that are of importance.

        self.board is a two dimensional array that stores each of the pieces
        in their respective locations.

        self.history is an array of the moves that have occurred so far. Any move
        is recorded by a call to the move_piece method. It is used by the
        undo_move method.

        self.en_passant points to the pawn that has moved two steps up and
        thus is "en passant"-able. That is, a pawn in the correct conditions
        may be able to take the pawn. 

        self.queen_side_castle and self.king_side_castle are dictionaries consisting
        of two keys WHITE and BLACK which tells whether the respective king may
        castle.

        >>> board = Board()
        >>> print(board.board[0][0].name)
        rook
        >>> print(board.board[0][0].color)
        0
        >>> print(board.board[0][1].name)
        knight
        >>> print(board.board[0][2].name)
        bishop
        >>> print(board.board[0][3].name)
        queen
        >>> print(board.board[0][4].name)
        king
        >>> print(board.board[7][0].color)
        1
        """
        if json:
            self.board = json["board"]
            self.kings = json["kings"]
            self.en_passant = Piece.from_json(json["en_passant"])
            self.queen_side_castle = json["queen_side_castle"]
            self.king_side_castle = json["king_side_castle"]

            for i in range(8):
                for j in range(8):
                    self.board[i][j] = Piece.from_json(self.board[i][j])
            return 

        self.board = [[None] * 8, [None] * 8, [None] * 8, [None] * 8,
                      [None] * 8, [None] * 8, [None] * 8, [None] * 8]
        self.kings = [None, None]
        self.en_passant = None
        self.queen_side_castle = [True, True]
        self.king_side_castle = [True, True]
       
        if not empty:
            # Populate board
            self.add_piece(all_pieces[ROOK][WHITE][0][0])
            self.add_piece(all_pieces[KNIGHT][WHITE][0][1])
            self.add_piece(all_pieces[BISHOP][WHITE][0][2])
            self.add_piece(all_pieces[QUEEN][WHITE][0][3])
            self.add_piece(all_pieces[KING][WHITE][0][4])
            self.add_piece(all_pieces[BISHOP][WHITE][0][5])
            self.add_piece(all_pieces[KNIGHT][WHITE][0][6])
            self.add_piece(all_pieces[ROOK][WHITE][0][7])

            self.add_piece(all_pieces[ROOK][BLACK][7][0])
            self.add_piece(all_pieces[KNIGHT][BLACK][7][1])
            self.add_piece(all_pieces[BISHOP][BLACK][7][2])
            self.add_piece(all_pieces[QUEEN][BLACK][7][3])
            self.add_piece(all_pieces[KING][BLACK][7][4])
            self.add_piece(all_pieces[BISHOP][BLACK][7][5])
            self.add_piece(all_pieces[KNIGHT][BLACK][7][6])
            self.add_piece(all_pieces[ROOK][BLACK][7][7])

            for i in range(8):
                self.add_piece(all_pieces[PAWN][WHITE][1][i])
                self.add_piece(all_pieces[PAWN][BLACK][6][i])

    def __str__(self):
        """
        Prints the board in the usual way.
        >>> print(Board())
            a   b   c   d   e   f   g   h
           --- --- --- --- --- --- --- ---
        8 | R | N | B | Q | K | B | N | R |
           --- --- --- --- --- --- --- ---
        7 | P | P | P | P | P | P | P | P |
           --- --- --- --- --- --- --- ---
        6 |   |   |   |   |   |   |   |   |
           --- --- --- --- --- --- --- ---
        5 |   |   |   |   |   |   |   |   |
           --- --- --- --- --- --- --- ---
        4 |   |   |   |   |   |   |   |   |
           --- --- --- --- --- --- --- ---
        3 |   |   |   |   |   |   |   |   |
           --- --- --- --- --- --- --- ---
        2 | p | p | p | p | p | p | p | p |
           --- --- --- --- --- --- --- ---
        1 | r | n | b | q | k | b | n | r |
           --- --- --- --- --- --- --- ---
            a   b   c   d   e   f   g   h
        """
        alpha = "abcdefgh"
        alpha_line = " "
        for i in alpha:
            alpha_line += "   " + i
        board = alpha_line

        border = "\n  " + " ---" * 8
        board += border
        for i in range(8, 0, -1):
            line = "\n{0} |".format(i)
            for j in self.board[i - 1]:
                if j is None:
                    line += "   |"
                elif Piece.use_unicode:
                    line += " " + j.get_unicode() + " |"
                elif j.color == WHITE:
                    line += " " + j.char.lower() + " |"
                else:
                    line += " " + j.char + " |"
            board += line
            board += border
        board += "\n" + alpha_line
        return board
    
    def compute_score(self, color):
        """
        Computes the score of the board given the color.
        :param color:
        :return:
        >>> board = Board()
        >>> board.compute_score(0)
        0
        >>> board.compute_score(1)
        0
        >>> board.remove_piece(locate("a2"))
        >>> board.compute_score(0)
        -1
        >>> board.compute_score(1)
        1
        """
        score = 0
        for i in range(8):
            for j in range(8):
                p = self.board[i][j]
                if p is None:
                    continue
                if p.color == color:
                    score += p.points
                else:
                    score -= p.points
        return score

    def get_piece(self, position):
        """
        Gets piece on board at given position.
        >>> board = Board()
        >>> board.get_piece(locate("a2")).name
        'pawn'
        >>> board.get_piece(locate("a1")).name
        'rook'
        >>> board.get_piece(locate("b1")).name
        'knight'
        >>> board.get_piece(locate("b1")).position == locate("b1")
        True
        """
        if not position.in_range():
            raise ValueError("no piece at {0}".format(position))
        return self.board[position.row][position.col]

    def add_piece(self, piece):
        """
        Adds piece on board at given position.
        >>> board = Board(empty=True)
        >>> board.add_piece(Pawn(WHITE, locate("d4")))
        >>> pawn = board.get_piece(locate("d4"))
        >>> pawn.name
        'pawn'
        >>> pawn.position
        d4
        """
        self.board[piece.position.row][piece.position.col] = piece

        # Record King
        if piece.name == "king":
            self.kings[piece.color] = piece
    
    def make_move(self, move):
        """
        Takes a move object and applies the move to the current board.
        """
        self.move_piece(move.piece, 
                move.position, 
                ep=move.ep, 
                castle=move.castle, 
                promote=move.promote)

    # TODO: Add more doctests and thoroughly describe what happens
    # in the docs.
    def move_piece(self, piece, position, ep=False, castle=False, promote=None):
        """
        Moves piece from initial to final position. Returns new piece.
        Note that pieces should be immutable. The ultimate goal of this 
        method is so that when we call move_piece on piece and position 
        such that piece.is_valid(position) and not board.in_check()
        then the resulting game should be completely valid. The condition 
        that piece.is_valid is called separately relaxes some of the rules
        and allows for moving pieces in a free style.

        The analogy could be made that move_piece is to a real player
        moving chess pieces in an arbitrary fashion, while following the 
        rules leads to a valid chess game.

        In addition, board.in_check() should be called after the move is 
        made since the move must be made in order to check for a check.

        Castling is an exception. When castling is specified, then the 
        method will make sure that King is not in check, does not go 
        through check, or does not go into check. When the pawn moves 
        en passant, then certain checks are done, but the method does 
        not ensure that the board is not in check. Promotion is similar.

        Parameters:
            piece -- The piece to be moved. Is an instace of Piece or
                its subclass.
            position -- The position to move to. Is an instacnce of 
                Position. 
        Optional Parameters:
            ep -- Whether the move is an en passant or not. True or False.
            castle -- Whether to castle or not. True or False.
            promote -- Piece to promote to, if the move is a promotion. 
                Default value is None.

        TODO: Currently, because all pieces are instantiated only once,
        it makes no sense to pass in piece and position. It seems to be
        more logical to pass in inital_position and final_position.
        I will probably need to think more about the whole structure of 
        this program and think about how to make this change.

        >>> board = Board()
        >>> bishop = board.get_piece(locate("c1"))
        >>> bishop.position
        c1
        >>> bishop.name
        'bishop'
        >>> bishop = board.move_piece(bishop, locate("f6"))
        >>> bishop.position
        f6
        >>> board.get_piece(locate("f6")) is bishop
        True
        >>> board.get_piece(locate("c1")) is None
        True
        """
        # Handle En passant
        if piece.name == "pawn":
            unit = 1 if piece.color == WHITE else -1
            start = 1 if piece.color == WHITE else 6
            if piece.position.row == start and position.row == start + 2 * unit:
                self.en_passant = all_pieces[piece.index][piece.color][position.row][position.col]
        else:
            self.en_passant = None

        # Handle Castling
        if piece.name == "king":
            self.queen_side_castle[piece.color] = False
            self.king_side_castle[piece.color] = False

        if piece.name == "rook" and piece.position.row == 0:
            self.queen_side_castle[piece.color] = False

        if piece.name == "rook" and piece.position.row == 7:
            self.king_side_castle[piece.color] = False
        
        # En passant
        if ep:
            if piece.index != PAWN:
                raise ValueError("only pawns may move en passant")
            target = self.get_piece(position + (-1, 0))
            if not target or target is not self.en_passant:
                raise ValueError("move is not en passant")
            target.remove_piece(target.position)

        # Castle
        if castle:
            if piece.index != KING:
                raise ValueError("only king may castle")
            if position.row != piece.position.row:
                raise ValueError("cannot castle king to this row")
            elif position.col == 3:
                if not self.queen_side_castle[piece.color]:
                    raise ValueError("cannot move since either rook or king\
                        has previously moved")
                unit = -1
            elif position.col == 7:
                if not self.king_side_castle[piece.color]:
                    raise ValueError("cannot move since either rook or king\
                            has previously moved")
                unit = 1
            else:
                raise ValueError("cannot castle king to this column")

            if self.in_check(piece.color):
                raise ValueError("cannot castle out of check")
            self.move_piece(piece, position + (0, unit))
            if self.in_check(piece.color):
                raise ValueError("cannot castle through check")
            self.move_piece(piece, position + (0, unit))
            if self.in_check(piece.color):
                raise ValueError("cannot castle into check")
            return

        # Move piece
        target = self.get_piece(position)
        if target:
            self.remove_piece(target.position)
        self.board[position.row][position.col] = all_pieces[piece.index][piece.color][position.row][position.col]
        self.board[piece.position.row][piece.position.col] = None
        if piece.index == KING:
            self.kings[piece.color] = self.board[position.row][position.col]
        # DEBUG!!!
        if Board.debug:
            assert(self.is_consistent)
        
        return self.board[position.row][position.col]

    def remove_piece(self, position):
        """
        Removes piece from board and returns a pointer to the piece.
        >>> board = Board()
        >>> board.remove_piece(locate("e2"))
        >>> board.get_piece(locate("e2")) is None
        True
        """
        self.board[position.row][position.col] = None
    
    def get_moves(self, turn, heuristic=None):
        """
        Returns a generator.
        :return:
        TODO IMPROVE !!!! AHHHH
        """
        if heuristic is None:
            heuristic = lambda a: 0
        priority_queue = utils.PriorityQueue()
        for i in range(8):
            for j in range(8):
                piece = self.get_piece(Position(i, j))
                if not piece or not piece.color == turn:
                    continue
                positions = piece.valid_pos(self)
                for p in positions:
                    move = Move(piece, p)
                    board_with_move = self.copy()
                    board_with_move.move_piece(move.piece, move.position)
                    priority_queue.queue(
                        heuristic(board_with_move),
                        (move, board_with_move))
        while not priority_queue.is_empty() > 0:
            yield priority_queue.pop()

    def in_check(self, color):
        """
        Returns true if the given player (color) is currently in check.
        >>> board = Board()
        >>> board.in_check(WHITE)
        False
        >>> board.in_check(BLACK)
        False
        >>> queen = board.get_piece(locate("d8"))
        >>> queen = board.move_piece(queen, locate("e2"))
        >>> board.in_check(WHITE)
        True
        >>> board.in_check(BLACK)
        False
        """
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None or piece.color == color:
                    continue
                if piece.is_valid(self.kings[color].position, self):
                    return True
        return False

    def is_consistent(self):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is not None:
                    assert(piece.position.row == i)
                    assert(piece.position.col == j)

    def copy(self):
        """
        TODO ADD DOCTESTS AND DOCSTRING
        :return:
        """
        board = Board(empty=True)
        board.board = []
        for row in self.board:
            board.board.append(row.copy())
        board.en_passant = self.en_passant
        board.kings = self.kings.copy()
        board.king_side_castle = self.king_side_castle.copy()
        board.queen_side_castle = self.queen_side_castle.copy()
        return board


# Pieces
class Piece:
    char = "*"
    use_unicode = True

    def __init__(self, color, position):
        """
        Constructs a piece. A piece has several important instance 
        variables.

        self.color is the piece's color.

        self.position is the piece's position, an instance of the 
        Position class.

        self.board is the board that the piece belongs to.
        >>> piece = Piece(BLACK, locate("a1"))
        >>> piece.color
        1
        """
        assert color == BLACK or color == WHITE
        self.color = color
        self.position = position
        self.index = self.index

    def from_json(json): 
        """Constructs a piece from the "json" representation."""
        if not json:
            return None
        types = [King, Queen, Rook, Bishop, Knight, Pawn]
        color = json["color"]
        position = Position(json["position"]["row"],
                json["position"]["col"])
        index = json["index"]
        
        piece = types[index](color, position)
        return piece

    def __str__(self):
        """
        Returns the string representation of Piece. It is given in
        the form "Piece_Name(color, position)". For example, a Rook object
        with color BLACK and position a1 will be represented as
        "Rook(BLACK, a1)".
        TODO: Update doctext
        >>> print(Piece(BLACK, locate("a8")))
        b*a8
        >>> print(Piece(WHITE, locate("a1")))
        w*a1
        """
        return "{0}{1}{2}".format("b" if self.color else "w",
                                  self.char, repr(self.position))

    def get_unicode(self):
        init = 0x2654
        if self.color == BLACK:
            init += 6
        init += self.index
        return chr(init)

    def __repr__(self):
        """
        Returns the representation of Piece. It is the same as
        the __str__ method.
        """
        return Piece.__str__(self)


class Pawn(Piece):
    name = "pawn"
    char = "P"
    points = 1
    index = 5

    def __init__(*args):
        """ Constructs a pawn.
        >>> pawn = Pawn(BLACK, locate("a2"))
        >>> pawn.name
        'pawn'
        >>> pawn.color
        1
        """
        Piece.__init__(*args)
    
    def is_valid(self, position, board):
        """
        Given a position to move to, validates the move based on board.
        >>> board = Board()
        >>> pawn1 = board.get_piece(locate("d2"))
        >>> pawn2 = board.get_piece(locate("e7"))
        >>> pawn3 = board.get_piece(locate("c7"))
        >>> pawn1.is_valid(locate("d3"), board) # Advance white pawn
        True
        >>> pawn1.is_valid(locate("d4"), board)
        True
        >>> pawn1.is_valid(locate("d5"), board)
        False
        >>> pawn1 = board.move_piece(pawn1, locate("d4"))
        >>> pawn2.is_valid(locate("d5"), board) # Advance white pawn
        False
        >>> pawn1.is_valid(locate("d6"), board)
        False
        >>> pawn2.is_valid(locate("e6"), board) # Advance black pawn
        True
        >>> pawn2.is_valid(locate("e5"), board)
        True
        >>> pawn2.is_valid(locate("e4"), board)
        False
        >>> pawn2 = board.move_piece(pawn2, locate("e5"))
        >>> pawn1.is_valid(locate("e5"), board) # Attack black pawn
        True
        >>> pawn2.is_valid(locate("d4"), board) # Attack white pawn
        True
        >>> pawn1 = board.move_piece(pawn1, locate("d5"))
        >>> pawn3 = board.move_piece(pawn3, locate("c5"))
        >>> pawn1.is_valid(locate("c6"), board)
        True
        """
        unit = 1 if self.color == WHITE else -1
        start = 1 if self.color == WHITE else 6
        target = board.get_piece(position)
        # Move one unit
        if position == self.position + (unit, 0) and not target:
            return True
        # Move two units
        if position == self.position + (2 * unit, 0)\
                and self.position.row == start\
                and not board.get_piece(self.position + (unit , 0))\
                and not target:
            return True
        # But most importantly, he attac
        if position == self.position + (unit, 1)\
                or position == self.position + (unit, -1):
            if target and target.color != self.color:
                return True
            mod_pos = position + (-unit, 0)
            if board.get_piece(mod_pos)\
                    and board.get_piece(mod_pos).color != self.color\
                    and board.get_piece(mod_pos) == board.en_passant:
                return True
        return False
    
    def valid_pos(self, board):
        """
        Outputs a list of valid positions to move to.
        >>> board = Board()
        >>> pawn1 = board.get_piece(locate("e2"))
        >>> pawn2 = board.get_piece(locate("d7"))
        >>> pawn1.valid_pos(board)
        [e3, e4]
        >>> pawn2.valid_pos(board)
        [d6, d5]
        >>> pawn1 = board.move_piece(pawn1, locate("e4"))
        >>> pawn2 = board.move_piece(pawn2, locate("d5"))
        >>> pawn1.valid_pos(board)
        [e5, d5]
        >>> pawn2.valid_pos(board)
        [d4, e4]
        """
        valid_pos = []
        unit = 1 if self.color == WHITE else -1
        start = 1 if self.color == WHITE else 6
        forward_one = self.position + (unit, 0)
        forward_two = self.position + (2 * unit, 0)
        
        # Move forward
        if not board.get_piece(forward_one):
            valid_pos.append(forward_one)
            if self.position.row == start\
                    and not board.get_piece(forward_two):
                valid_pos.append(forward_two)
        
        # Attack
        attack_pos = [self.position + (unit, -1), self.position + (unit, 1)]
        for p in attack_pos:
            if not p.in_range():
                continue
            ep = p + (-unit, 0)
            if board.get_piece(p)\
                    and board.get_piece(p).color != self.color:
                valid_pos.append(p)
            elif board.get_piece(ep)\
                    and board.get_piece(ep) is board.en_passant:
                valid_pos.append(p)

        return valid_pos


class Bishop(Piece):
    name = "bishop"
    char = "B"
    points = 3
    index = BISHOP

    def __init__(*args):
        Piece.__init__(*args)

    def is_valid(self, position, board):
        """
        Returns True if move to position is valid.
        >>> board = Board()
        >>> pawn1 = board.get_piece(locate("e2"))
        >>> pawn2 = board.get_piece(locate("b7"))
        >>> bishop = board.get_piece(locate("f1"))
        >>> pawn1 = board.move_piece(pawn1, locate("e4")) # Move ally pawn up
        >>> bishop.is_valid(locate("b5"), board) # Valid move
        True
        >>> pawn2 = board.move_piece(pawn2, locate("b5")) # Move enemy pawn up
        >>> bishop.is_valid(locate("b5"), board) # Not correct
        True
        >>> bishop.is_valid(locate("g2"), board) # Blocked
        False
        >>> bishop.is_valid(locate("h3"), board) # Blocked again
        False
        >>> bishop.is_valid(locate("h4"), board) # Not a diagonal
        False
        """
        if piece_is_blocked_diagonal(self, position, board):
            return False
        target = board.get_piece(position)
        if target and target.color == self.color:
            return False
        return True

    def valid_pos(self, board):
        """
        Returns the possible position for self (bishop) to move.
        >>> board = Board()
        >>> bishop = board.get_piece(locate("f1"))
        >>> pawn = board.get_piece(locate("e2"))
        >>> bishop.valid_pos(board)
        []
        >>> pawn = board.move_piece(pawn, locate("e3"))
        >>> bishop.valid_pos(board)
        [e2, d3, c4, b5, a6]
        >>> bishop = board.move_piece(bishop, locate("d3"))
        >>> bishop.valid_pos(board)
        [e4, f5, g6, h7, c4, b5, a6, e2, f1]
        """
        valid_pos = []
        for unit in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            cur = self.position
            while True:
                cur = cur + unit
                if not cur.in_range():
                    break
                piece = board.get_piece(cur)
                if piece:
                    if piece.color != self.color:
                        valid_pos.append(cur)
                    break
                
                valid_pos.append(cur)
        return valid_pos

class Knight(Piece): 
    name = "knight"
    char = "N"
    points = 3
    index = KNIGHT

    def __init__(*args):
        Piece.__init__(*args)

    def is_valid(self, position, board):
        """
        Returns True if move to position is valid.
        >>> board = Board()
        >>> knight = board.get_piece(locate("b1"))
        >>> knight.is_valid(locate("b1"), board)
        False
        >>> knight.is_valid(locate("c3"), board)
        True
        >>> knight.is_valid(locate("d2"), board)
        False
        >>> knight.is_valid(locate("d4"), board)
        False
        >>> knight.is_valid(locate("a3"), board)
        True
        """
        row_change = abs(self.position.row - position.row)
        col_change = abs(self.position.col - position.col)
        if not (row_change == 2 and col_change == 1 or\
                row_change == 1 and col_change == 2):
            return False
        target = board.get_piece(position)
        if target and target.color == self.color:
            return False
        return True

    def valid_pos(self, board):
        """
        Returns a list of valid positions for self (knight) to move to.
        >>> board = Board()
        >>> knight = board.get_piece(locate("b1"))
        >>> knight.valid_pos(board)
        [c3, a3]
        >>> knight = board.move_piece(knight, locate("c3"))
        >>> knight.valid_pos(board)
        [e4, d5, b5, a4, b1]
        >>> knight = board.move_piece(knight, locate("b5"))
        >>> knight.valid_pos(board)
        [d6, c7, d4, a7, c3, a3]
        """
        valid_pos = []

        for unit in [(1, 2), (2, 1), (-1, 2), (2, -1),
                (1, -2), (-2, 1), (-1, -2), (-2, -1)]:
            cur = self.position + unit
            if not cur.in_range():
                continue
            piece = board.get_piece(cur)
            if piece and piece.color == self.color:
                continue
            valid_pos.append(cur)
        
        return valid_pos

class Rook(Piece):
    name = "rook"
    char = "R"
    points = 5
    index = ROOK

    def __init__(*args):
        Piece.__init__(*args)

    def is_valid(self, position, board):
        """Returns True if move to position is valid
        >>> board = Board(empty=True)
        >>> rook = Rook(BLACK, locate("d4"))
        >>> board.add_piece(rook)
        >>> board.add_piece(Pawn(WHITE, locate("d2")))
        >>> board.add_piece(Pawn(WHITE, locate("b4")))
        >>> rook.is_valid(locate("d2"), board)
        True
        >>> rook.is_valid(locate("d1"), board)
        False
        >>> rook.is_valid(locate("d3"), board)
        True
        >>> rook.is_valid(locate("d4"), board)
        False
        >>> rook.is_valid(locate("a4"), board)
        False
        >>> rook.is_valid(locate("b4"), board)
        True
        >>> rook.is_valid(locate("b3"), board)
        False
        """
        if piece_is_blocked_straight(self, position, board):
            return False
        target = board.get_piece(position)
        if target and target.color == self.color:
            return False
        return True
    
    def valid_pos(self, board):
        """
        Returns the valid moves for rook.
        >>> board = Board()
        >>> board.remove_piece(locate("a2"))
        >>> rook = board.get_piece(locate("a1"))
        >>> rook.valid_pos(board)
        [a2, a3, a4, a5, a6, a7]
        >>> rook = board.move_piece(rook, locate("a4"))
        >>> rook.valid_pos(board)
        [a5, a6, a7, b4, c4, d4, e4, f4, g4, h4, a3, a2, a1]
        >>> rook = board.move_piece(rook, locate("d4"))
        >>> rook.valid_pos(board)
        [d5, d6, d7, e4, f4, g4, h4, d3, c4, b4, a4]
        """
        valid_pos = []
        for unit in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            cur = self.position
            while True:
                cur = cur + unit
                if not cur.in_range():
                    break
                piece = board.get_piece(cur)
                if piece:
                    if piece.color != self.color:
                        valid_pos.append(cur)
                    break
                
                valid_pos.append(cur)
        return valid_pos

class Queen(Piece):
    name = "queen"
    char = "Q"
    points = 9
    index = QUEEN

    def __init__(*args):
        Piece.__init__(*args)
    
    # TODO: Finish doctests
    def is_valid(self, position, board):
        """
        Returns True if move to position is valid.
        """
        if piece_is_blocked_straight(self,position, board) and\
                piece_is_blocked_diagonal(self, position, board):
            return False
        if board.get_piece(position) and\
                board.get_piece(position).color == self.color:
            return False
        return True

    def valid_pos(self, board):
        valid_pos = []
        for unit in [(1, 0), (0, 1), (-1, 0), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            cur = self.position
            while True:
                cur = cur + unit
                if not cur.in_range():
                    break
                piece = board.get_piece(cur)
                if piece:
                    if piece.color != self.color:
                        valid_pos.append(cur)
                    break
                
                valid_pos.append(cur)
        return valid_pos


# TODO: Implement castling
class King(Piece):
    name = "king"
    char = "K"
    points = 9001
    index = KING

    def __init__(*args):
        Piece.__init__(*args)
    
    # TODO: Finish doctests
    def is_valid(self, position, board):
        """
        Returns True if move to position is valid.
        >>> board = Board()
        >>> board.remove_piece(locate("e2"))
        >>> king = board.kings[WHITE]
        >>> king.is_valid(locate("e2"), board)
        True
        >>> king.is_valid(locate("e3"), board)
        False
        >>> king.is_valid(locate("d1"), board)
        False
        """
        row_change = abs(position.row - self.position.row)
        col_change = abs(position.col - self.position.col)

        if row_change == 0 and col_change == 0:
            return False
        if row_change > 1 or col_change > 1:
            return False
        if board.get_piece(position) and\
                board.get_piece(position).color == self.color:
            return False
        return True
    
    # TODO: Add doctests
    # TODO: Implement castling
    # TODO: Finish
    def valid_pos(self, board):
        """
        Returns the valid positions for the king.
        >>> board = Board(empty=True)
        >>> board.add_piece(Rook(WHITE, locate("a1")))
        >>> board.add_piece(Rook(WHITE, locate("h1")))
        >>> board.add_piece(King(WHITE, locate("e1")))
        >>> board.add_piece(Rook(BLACK, locate("a8")))
        >>> king = board.kings[WHITE]
        >>> king.valid_pos(board)
        [e2, f2, f1, d1, d2]
        """
        valid_pos = []
        for unit in [(1, 0), (1, 1), (0, 1), (-1, 1),
                (-1, 0), (-1, -1), (0, -1), (1, -1)]:
            cur = self.position + unit
            if not cur.in_range():
                continue
            target = board.get_piece(cur)
            if not target or target.color != self.color:
                valid_pos.append(cur)

        return valid_pos


all_pieces = generate_all_pieces()
