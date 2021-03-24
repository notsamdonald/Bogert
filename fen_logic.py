import fen_settings as s


def decode_fen(fen: str) -> dict:
    """
    Decodes a fen into a dictionary containing ??? TODO  fill this out once complete
    :param fen: string
    :return:
    """

    board = {}
    # splitting the fen into parts
    square_data, turn, castling_rights, en_passant, half_turn, full_turn = fen.split(" ")
    square_data = square_data.replace('/', '')

    # Create an empty board
    for square in range(s.board_square_count):
        if square in s.real_board_squares:
            board[square] = "--"  # on the board
        else:
            board[square] = "FF"  # not on the board

    # Populating board with fen data
    square_index = 0
    for square_content in square_data:
        if square_content.isdigit():
            square_index += int(square_content)  # step over the number of squares
        else:
            board_index = s.real_board_squares[square_index]
            board[board_index] = s.fen_to_piece[square_content]
            square_index += 1  # increment for next insertion

    # Processing en_passant square
    if en_passant == "-":
        en_passant_square = None
    else:
        en_passant_square = s.algebraic_to_square_id[en_passant]

    # Tidy of is_white_turn, half_turn, full_turn data
    is_whites_turn = True if turn == 'w' else False
    half_turn = int(half_turn)
    full_turn = int(full_turn)

    return board, castling_rights, en_passant_square, half_turn, full_turn, is_whites_turn