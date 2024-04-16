"""
Handling the AI moves.
"""
import random
from ChessSet import ChessSet

piece_score = {"k": 0, "q": 9, "r": 5, "b": 3, "n": 3, "p": 1}

knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
               [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
               [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
               [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
               [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
               [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
               [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
               [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piece_position_scores = {"Wn": knight_scores,
                         "Bn": knight_scores[::-1],
                         "Wb": bishop_scores,
                         "Bb": bishop_scores[::-1],
                         "Wq": queen_scores,
                         "Bq": queen_scores[::-1],
                         "Wr": rook_scores,
                         "Br": rook_scores[::-1],
                         "Wp": pawn_scores,
                         "Bp": pawn_scores[::-1]}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findBestMove(set: ChessSet, valid_moves, num_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    findMoveNegaMaxAlphaBeta(set, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if num_moves % 2 == 0 else -1, num_moves)
    return next_move


def findMoveNegaMaxAlphaBeta(set, valid_moves, depth, alpha, beta, turn_multiplier, num_moves):
    global next_move
    if depth == 0:
        return turn_multiplier * scoreBoard(set, num_moves)
    # move ordering - implement later //TODO
    max_score = -CHECKMATE
    for move in valid_moves:
        move.do(num_moves)
        if move.flag == "P": move.promote(move.piece.color + "q")
        num_moves += 1
        set.generate_legal_moves("W" if num_moves % 2 == 0 else "B", num_moves)
        score = -findMoveNegaMaxAlphaBeta(set, set.flattened, depth - 1, -beta, -alpha, -turn_multiplier, num_moves)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        move.undo()
        num_moves -= 1
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def scoreBoard(set, num_moves):
    # print("scoring")
    """
    Score the board. A positive score is good for white, a negative score is good for black.
    """
    color = "W" if num_moves % 2 == 0 else "B"
    if set.no_moves and set.check_check(color):
        if color == "W":
            return -CHECKMATE  # black wins
        else:
            return CHECKMATE  # white wins
    elif set.no_moves:
        return STALEMATE
    score = 0
    for row in range(len(set.grid)):
        for col in range(len(set.grid[row])):
            piece = set.grid[row][col]
            if piece:
                piece_position_score = 0
                if piece.piece != "k":
                    piece_position_score = piece_position_scores[piece.color + piece.piece][row][col]
                if piece.color == "W":
                    score += piece_score[piece.piece] + piece_position_score
                if piece.color == "B":
                    score -= piece_score[piece.piece] + piece_position_score

    # print(score)
    return score


def findRandomMove(valid_moves):
    """
    Picks and returns a random valid move.
    """
    return random.choice(valid_moves)
