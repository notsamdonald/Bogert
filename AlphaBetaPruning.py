import chess
import math
import random
import sys
import time
from numba import jit

BOUNDS_DICT = {
    "P": [0, 0, 0, 0, 0, 0, 0, 0,
          50, 50, 50, 50, 50, 50, 50, 50,
          10, 10, 20, 30, 30, 20, 10, 10,
          5, 5, 10, 25, 25, 10, 5, 5,
          0, 0, 0, 20, 20, 0, 0, 0,
          5, -5, -10, 0, 0, -10, -5, 5,
          5, 10, 10, -20, -20, 10, 10, 5,
          0, 0, 0, 0, 0, 0, 0, 0],

    "N": [-50, -40, -30, -30, -30, -30, -40, -50,
          -40, -20, 0, 0, 0, 0, -20, -40,
          -30, 0, 10, 15, 15, 10, 0, -30,
          -30, 5, 15, 20, 20, 15, 5, -30,
          -30, 0, 15, 20, 20, 15, 0, -30,
          -30, 5, 10, 15, 15, 10, 5, -30,
          -40, -20, 0, 5, 5, 0, -20, -40,
          -50, -40, -30, -30, -30, -30, -40, -50, ],

    "B": [-20, -10, -10, -10, -10, -10, -10, -20,
          -10, 0, 0, 0, 0, 0, 0, -10,
          -10, 0, 5, 10, 10, 5, 0, -10,
          -10, 5, 5, 10, 10, 5, 5, -10,
          -10, 0, 10, 10, 10, 10, 0, -10,
          -10, 10, 10, 10, 10, 10, 10, -10,
          -10, 5, 0, 0, 0, 0, 5, -10,
          -20, -10, -10, -10, -10, -10, -10, -20, ],

    "R": [0, 0, 0, 0, 0, 0, 0, 0,
          5, 10, 10, 10, 10, 10, 10, 5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          -5, 0, 0, 0, 0, 0, 0, -5,
          0, 0, 0, 5, 5, 0, 0, 0],

    "Q": [-20, -10, -10, -5, -5, -10, -10, -20,
          -10, 0, 0, 0, 0, 0, 0, -10,
          -10, 0, 5, 5, 5, 5, 0, -10,
          -5, 0, 5, 5, 5, 5, 0, -5,
          0, 0, 5, 5, 5, 5, 0, -5,
          -10, 5, 5, 5, 5, 5, 0, -10,
          -10, 0, 5, 0, 0, 0, 0, -10,
          -20, -10, -10, -5, -5, -10, -10, -20],

    "K": [-30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -30, -40, -40, -50, -50, -40, -40, -30,
          -20, -30, -30, -40, -40, -30, -30, -20,
          -10, -20, -20, -20, -20, -20, -20, -10,
          20, 20, 0, 0, 0, 0, 20, 20,
          20, 30, 10, 0, 0, 10, 30, 20]}


def minimaxRoot(depth, board, is_maximizing, square_bonus=False, iterative_deeping=True):
    tic = time.perf_counter()

    #possible_moves = random_possible_move(board)
    board.get_all_possible_moves()
    possible_moves = board.possible_moves

    best_move_score = -9999 if is_maximizing else 9999
    best_move = None
    move_count = 0

    if iterative_deeping:
        move_score_array = []
        for move in possible_moves:
            move_score_array.append([move, (evaluation(board, square_bonus=False))])
        move_score_array = sorted(move_score_array, key=lambda x: x[1])
        if is_maximizing:
            move_score_array.reverse()

        possible_moves = [item[0] for item in move_score_array]

    for x in possible_moves:
        move = chess.Move.from_uci(str(x))
        move_count += 1

        board.push(move)
        proposed_move_score, sub_tree_moves = minimax(depth=depth - 1,
                                                      board=board,
                                                      alpha=-10000,
                                                      beta=10000,
                                                      is_maximizing=not is_maximizing,
                                                      square_bonus=square_bonus)
        """
        proposed_move_score = negamax(depth=depth - 1,
                                      board=board,
                                      alpha=-10000,
                                      beta=10000,
                                      color=not is_maximizing)
        """
        move_count += sub_tree_moves

        if is_maximizing:
            value = max(best_move_score, proposed_move_score)
            if value > best_move_score:
                best_move_score = value
                best_move = move
            # print("Best score: ", str(best_move_score))
            # print("Best move: ", str(best_move_final))
        else:
            value = min(best_move_score, proposed_move_score)
            if value < best_move_score:
                best_move_score = value
                best_move = move
                # print("Best score: " ,str(best_move_score))
                # print("Best move: ",str(best_move_final))

        board.pop()  # Take away the proposed move
    toc = time.perf_counter()

    print("Best score: ", str(best_move_score))
    print("Best move: ", str(best_move))
    print("Moves evaluated: ", str(move_count))
    print("Evals/sec: {0:.1f}".format(move_count / (toc - tic)))
    print("Time: {0:.1f}s".format((toc - tic)))

    return best_move


def random_possible_move(board, random_suffle=False, ):
    possible_moves = list(board.legal_moves)
    if random_suffle:
        random.shuffle(possible_moves)
    return possible_moves


#@profile
def minimax(depth, board, alpha, beta, is_maximizing, square_bonus, iterative_deeping=True):
    # Reaching the maximum depth specified
    if depth == 0:
        # TODO - confused why the 'base' evaluation within the branch is always negated - assumed its wrt is_maximizing
        return evaluation(board, square_bonus), 0  # currently a simple summation of piece values
        # Fixme (59.3% of time spent here) ^

    possible_moves = random_possible_move(board)

    # Iterative deepening (TODO - confirm this is actually making improvements, should be ~10%)
    # FIXME - nope, slows it way way down in terms of evals/sec (probably increases pruning count though?)
    #  -> the implementation is slow?

    if iterative_deeping and depth > 1:
        move_score_array = []
        for move in possible_moves:
            move_score_array.append([move, (evaluation(board, square_bonus=False))])  # Fixme (21.5% of time spent here)
        move_score_array = sorted(move_score_array, key=lambda x: x[1])
        if is_maximizing:
            move_score_array.reverse()
        possible_moves = [item[0] for item in move_score_array]

    best_move_score = -9999 if is_maximizing else 9999
    best_move = None
    move_count = 0
    for move_str in possible_moves:
        move_count += 1
        move = chess.Move.from_uci(str(move_str))
        board.push(move)

        # Move down branch, switching turn and passing down alpha, beta
        # TODO - a bit confused about the structure and direction of this graph, kinda opposite to video I saw
        proposed_move_score, sub_tree_moves = minimax(depth - 1, board, alpha, beta, not is_maximizing, square_bonus)
        move_count += sub_tree_moves

        if is_maximizing:

            if proposed_move_score > best_move_score:
                best_move_score = max(best_move_score, proposed_move_score)
                alpha = max(alpha, best_move_score)  # Update alpha if best_move is better (higher) then prior alpha
                best_move = move

        else:
            if proposed_move_score < best_move_score:
                best_move_score = min(best_move_score, proposed_move_score)
                beta = min(beta, best_move_score)  # Update beta if best_move is better (lower) then prior beta
                best_move = move

        board.pop()  # Take away the proposed move

        # TODO - confused about this end condition for the branch
        if beta <= alpha:  #
            # print('pruned!')
            return best_move_score, move_count

    return best_move_score, move_count


def negamax(depth, board, alpha, beta, color):
    if depth == 0:
        return evaluation(board)
    leg_moves = board.legal_moves
    for i_move in leg_moves:
        move = chess.Move.from_uci(str(i_move))
        board.push(move)
        value = -negamax(depth - 1, board, -beta, -alpha, -color)
        board.pop()
        alpha = max(alpha, value)
        if beta <= alpha:
            return value
    return value


#@profile
def evaluation(board, square_bonus=True):
    board_total = 0
    piece_map = board.piece_map2()
    for square_id, piece in piece_map.items():
        # for i in range(64):
        # piece = board.piece_at(i)
        # if piece is not None:

        # Unpacking
        piece_str = piece.symbol()
        # piece_str = chess.piece_symbol(board.piece_at(square_id).piece_type)
        color = piece.color

        sign = 1 if color else -1
        board_total += sign * (getPieceValue(piece_str) + getPieceSqauareBonus(piece_str, square_id, color))

    return board_total


def getPieceValue(piece):
    if piece is None:
        return 0

    # TODO - make this more robust so it doesn't break if something weird is passed
    # https://www.chessprogramming.org/Simplified_Evaluation_Function#Piece_Values
    piece_dict = {"P": 100,
                  "N": 320,
                  "B": 330,
                  "R": 500,
                  "Q": 900,
                  "K": 20000}

    return piece_dict[piece.upper()]


def getPieceSqauareBonus(piece, position, is_maximizing):
    if not is_maximizing:
        position = 63 - position
    pos = 64 - (position // 8 + 1) * 8 + position - (position // 8) * 8  # TODO - fix this, think it is wrong!
    # print(piece, position,pos, bonus_dict[piece.upper()][pos])
    return BOUNDS_DICT[piece.upper()][pos]


def main():
    board = chess.Board()
    n = 0
    print(board)
    while n < 100:
        if n % 2 == 0:
            move = input("Enter move: ")
            move = chess.Move.from_uci(str(move))
            print(move)
            board.push(move)
        else:
            print("Computers Turn:")
            move = minimaxRoot(3, board, True)
            move = chess.Move.from_uci(str(move))
            board.push(move)
            print(move)
        print(board)
        n += 1


if __name__ == "__main__":
    main()
