import chess
import math
import random
import sys


def minimaxRoot(depth, board, is_maximizing):
    possible_moves = random_possible_move(board)
    best_move = -9999 if is_maximizing else 9999
    best_move_final = None
    for x in possible_moves:
        move = chess.Move.from_uci(str(x))

        print(move)
        board.push(move)

        proposed_move = minimax(depth=depth - 1,
                                board=board,
                                alpha=-10000,
                                beta=-10000,
                                is_maximizing=not is_maximizing)

        if is_maximizing:
            value = max(best_move, proposed_move)
            if value > best_move:
                best_move = value
                best_move_final = move
                print("Best score: ", str(best_move))
                print("Best move: ", str(best_move_final))
        else:
            value = min(best_move, proposed_move)
            if value < best_move:
                best_move = value
                best_move_final = move
                print("Best score: " ,str(best_move))
                print("Best move: ",str(best_move_final))

        board.pop()  # Take away the proposed move

    return best_move_final


def random_possible_move(board):

    possible_moves = list(board.legal_moves)
    random.shuffle(possible_moves)
    return possible_moves


def minimax(depth, board, alpha, beta, is_maximizing):

    # Reaching the maximum depth specified
    if depth == 0:
        # TODO - confused why the 'base' evaluation within the branch is always negated - assumed its wrt is_maximizing
        return -evaluation(board, is_maximizing)  # currently a simple summation of piece values

    possible_moves = random_possible_move(board)
    best_move = -9999 if is_maximizing else 9999
    for move_str in possible_moves:

        move = chess.Move.from_uci(str(move_str))
        board.push(move)

        # Move down branch, switching turn and passing down alpha, beta
        # TODO - a bit confused about the structure and direction of this graph, kinda opposite to video I saw
        move = minimax(depth - 1, board, alpha, beta, not is_maximizing)

        if is_maximizing:
            best_move = max(best_move, move)
            alpha = max(alpha, best_move)  # Update alpha if best_move is better (higher) then prior alpha
        else:
            best_move = min(best_move, move)
            beta = min(beta, best_move)  # Update beta if best_move is better (lower) then prior beta

        board.pop()  # Take away the proposed move

        # TODO - confused about this end condition for the branch
        if beta <= alpha:  #
            return best_move

    return best_move


def evaluation(board, is_maximizing):

    board_total = 0

    for i in range(64):

        try:
            color = board.piece_at(i).color
        except AttributeError as e:
            color = None

        if color is not None:
            if board.piece_at(i).color:  # White
                board_total += getPieceValue(str(board.piece_at(i)))
            else:  # Black
                board_total -= getPieceValue(str(board.piece_at(i)))

    return board_total


def getPieceValue(piece):

    if piece is None:
        return 0

    # TODO - make this more robust so it doesn't break if something weird is passed
    piece_dict = {"P": 10,
                  "N": 30,
                  "B": 30,
                  "R": 50,
                  "Q": 90,
                  "K": 900}

    return piece_dict[piece.upper()]


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