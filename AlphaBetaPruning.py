import chess
import math
import random
import sys


def minimaxRoot(depth, board, is_maximizing, square_bonus = False):
    possible_moves = random_possible_move(board)
    best_move_score = -9999 if is_maximizing else 9999
    best_move = None
    move_count = 0
    for x in possible_moves:
        move = chess.Move.from_uci(str(x))
        move_count += 1

        board.push(move)
        proposed_move_score, sub_tree_moves = minimax(depth=depth - 1,
                                       board=board,
                                       alpha=-10000,
                                       beta=10000,
                                       is_maximizing = not is_maximizing,
                                                      square_bonus = square_bonus)
        move_count += sub_tree_moves

        if is_maximizing:
            value = max(best_move_score, proposed_move_score)
            if value > best_move_score:
                best_move_score = value
                best_move = move
               # print("Best score: ", str(best_move_score))
                #print("Best move: ", str(best_move_final))
        else:
            value = min(best_move_score, proposed_move_score)
            if value < best_move_score:
                best_move_score = value
                best_move = move
                #print("Best score: " ,str(best_move_score))
                #print("Best move: ",str(best_move_final))

        board.pop()  # Take away the proposed move

    print("Best score: ", str(best_move_score))
    print("Best move: ", str(best_move))
    print("Moves evaluated: ", str(move_count))

    return best_move


def random_possible_move(board):

    possible_moves = list(board.legal_moves)
    random.shuffle(possible_moves)
    return possible_moves


def minimax(depth, board, alpha, beta, is_maximizing, square_bonus):
    # Reaching the maximum depth specified
    if depth == 0:
        # TODO - confused why the 'base' evaluation within the branch is always negated - assumed its wrt is_maximizing
        return evaluation(board, square_bonus) , 0 # currently a simple summation of piece values

    possible_moves = random_possible_move(board)
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
            #print('pruned!')
            return best_move_score, move_count

    return best_move_score, move_count


def evaluation(board, square_bonus):

    board_total = 0

    for i in range(64):

        try:
            color = board.piece_at(i).color
        except AttributeError as e:
            color = None

        if color is not None:
            if board.piece_at(i).color:  # White
                board_total += getPieceValue(str(board.piece_at(i)))
                if square_bonus:
                    board_total += getPieceSqauareBonus(str(board.piece_at(i)), i, True)

            else:  # Black
                board_total -= (getPieceValue(str(board.piece_at(i))) + getPieceSqauareBonus(str(board.piece_at(i)), i, False))
                if square_bonus:
                    board_total -= getPieceSqauareBonus(str(board.piece_at(i)), i, False)

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

    bonus_dict = {
        "P": [ 0,  0,  0,  0,  0,  0,  0,  0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                 5,  5, 10, 25, 25, 10,  5,  5,
                 0,  0,  0, 20, 20,  0,  0,  0,
                 5, -5,-10,  0,  0,-10, -5,  5,
                 5, 10, 10,-20,-20, 10, 10,  5,
                 0,  0,  0,  0,  0,  0,  0,  0],

        "N" : [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50,],

        "B" : [-20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20,],

        "R" : [  0,  0,  0,  0,  0,  0,  0,  0,
                  5, 10, 10, 10, 10, 10, 10,  5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                 -5,  0,  0,  0,  0,  0,  0, -5,
                  0,  0,  0,  5,  5,  0,  0,  0],

        "Q" : [-20,-10,-10, -5, -5,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5,  5,  5,  5,  0,-10,
                 -5,  0,  5,  5,  5,  5,  0, -5,
                  0,  0,  5,  5,  5,  5,  0, -5,
                -10,  5,  5,  5,  5,  5,  0,-10,
                -10,  0,  5,  0,  0,  0,  0,-10,
                -20,-10,-10, -5, -5,-10,-10,-20],

        "K": [-30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -30,-40,-40,-50,-50,-40,-40,-30,
                -20,-30,-30,-40,-40,-30,-30,-20,
                -10,-20,-20,-20,-20,-20,-20,-10,
                 20, 20,  0,  0,  0,  0, 20, 20,
                 20, 30, 10,  0,  0, 10, 30, 20]}

    if not is_maximizing:
        position = 63 - position
    pos = 64 - (position//8 + 1) * 8 + position-(position//8)*8  # TODO - fix this, think it is wrong!
    #print(piece, position,pos, bonus_dict[piece.upper()][pos])
    return bonus_dict[piece.upper()][pos]


def main():
    board = chess.Board()
    n = 0
    print(board)
    while n < 100:
        if n%2 == 0:
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