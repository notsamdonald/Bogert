import fen_logic as fl
import fen_settings as s
import config as c
import random


class GameInstance:
    def __init__(self, starting_fen):

        self.starting_fen = starting_fen
        self.board, self.castling_rights, self.en_passant_square, self.half_move, self.full_move, self.is_whites_turn =\
            fl.decode_fen(self.starting_fen)

        self.piece_dict = self.initialize_piece_dict()
        self.initialize_piece_count_dict()
        self.rook_columns_list, self.pawn_columns_list = [[], []], [[], []]
        self.init_piece_columns()

        # Fixme - must be a better way then calling the function + adding it here?
        self.game_constants = {"A": [self.game_constant_A(), self.game_constant_A],
                               "B": [self.game_constant_B(), self.game_constant_B]}
        self.update_game_constants()

        # Piece values (# note - currently just a running tally of the evaluation func for each piece)
        self.piece_values = {'w': 0, 'b': 0}
        self.init_piece_values()

        # Init king positions
        self.has_castled = {'w': False, 'b': False}
        self.king_location = {'w': 0, 'b': 0}  # TODO - think about a better way to store this data vs multiple dicts
        self.init_king_positions()  # TODO - think it would be good to have this done for all pieces

        # Get possible moves for a certain piece type
        self.possible_moves = []
        self.move_functions = {'p': self.get_pawn_moves,
                               'N': self.get_knight_moves,
                               'B': self.get_bishop_moves,
                               'R': self.get_rook_moves,
                               'Q': self.get_queen_moves,
                               'K': self.get_king_moves}


        self.turn = self.update_turn()

        self.get_all_possible_moves()
        print('done!')

    def get_legal_moves(self):
        self.get_all_possible_moves()
        return self.possible_moves


    def make_move(self, move):

        # unpacking FIXME - don't like how unclear this is
        [start_square, end_square, move_type, delta_eval] = move

        piece_moved = self.board[start_square]
        piece_captured = self.board[end_square]

        self.board[end_square] = piece_moved
        self.board[start_square] = '--'

        self.turn_over()

    def turn_over(self):
        self.is_whites_turn = not self.is_whites_turn
        self.turn = self.update_turn()

    def update_turn(self):
        return 'w' if self.is_whites_turn else 'b'

    def get_all_possible_moves(self):
        """
        Get pseudo legal moves (without considering checks)
        :return:
        """
        moves = []
        for square in s.real_board_squares:
            color, piece = self.get_square_info(square)
            if piece in s.valid_pieces and self.turn == color:
                # checking if piece owned by the turn taker is present on the square
                self.move_functions[piece](square, moves)
        self.possible_moves = moves


    def get_pawn_moves(self, square, moves):
        pass

    def get_knight_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.knight_moves:
            end_square = square + direction   # moving in the direction one step
            color_s, piece_s = self.get_square_info(square)  # start square conents
            color_e, piece_e = self.get_square_info(end_square)  # end square contents

            if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                # TODO - implement pin check logic
                #if not piece_pinned or pin_direction in (d, -d):  #

                # note - calculating the increase in piece value based on move and game phase
                # TODO - increase this such that there are multiple tables extrapolated between based on phase
                piece_increase = (s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                # note - start/end sqaure - no (TODO  what this this)
                # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                # note - these are not needed for knight as not a sliding piece
                # note - if the end_square houses a enemy piece - stop checking in that direction.
                #if color_e == enemy_color:
                #    break  # break out of that direction
            #else:
            #    break

    def get_bishop_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.diagonal_dirs:
            for i in range(1, 8):
                end_square = square + direction * i  # moving in the direction one step
                color_s, piece_s = self.get_square_info(square)  # start square conents
                color_e, piece_e = self.get_square_info(end_square)  # end square contents

                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    #if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (s.piece_value_mid_game['R'][end_square] - s.piece_value_mid_game['R'][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                    # note - if the end_square houses a enemy piece - stop checking in that direction.
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break

    def get_rook_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.linear_dirs:
            for i in range(1, 8):
                end_square = square + direction * i  # moving in the direction one step
                color_s, piece_s = self.get_square_info(square)  # start square conents
                color_e, piece_e = self.get_square_info(end_square)  # end square contents

                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    #if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                    # note - if the end_square houses a enemy piece - stop checking in that direction.
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break

    def get_queen_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.diagonal_dirs + s.linear_dirs:
            for i in range(1, 8):
                end_square = square + direction * i  # moving in the direction one step
                color_s, piece_s = self.get_square_info(square)  # start square conents
                color_e, piece_e = self.get_square_info(end_square)  # end square contents

                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    #if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                    # note - if the end_square houses a enemy piece - stop checking in that direction.
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break

    def get_king_moves(self, square, moves):
        pass

    def init_king_positions(self):
        """
        Finds the locations of the kings (assumes only 2!) and updates the king location dictionary for each color
        """
        for square in self.board:
            color, piece = self.get_square_info(square)
            if piece == 'K':
                self.king_location[color] = square

    def init_piece_values(self):
        """
        Sets the starting values of the two piece value
        Fixme - wonder if using a dict here is slower? doubt it
        :return:
        """
        for square in self.board:
            color, piece = self.get_square_info(square)
            if color in s.valid_colors:
                # TODO - include the square bonus here (will have to invert black position to use 1 board)
                self.piece_values[color] += c.piece_value[piece]


    def initialize_piece_count_dict(self):
        """
        Iterates through self.board and initializes the number of pieces within piece dict (assumes values are at 0)
        :return: None
        """
        for square, piece_data in self.board.items():
            color = piece_data[0]
            piece = piece_data[1]

            if piece in s.valid_pieces:
                if color == 'b':
                    self.piece_dict[1][piece] += 1
                else:
                    self.piece_dict[0][piece] += 1
        return None

    @staticmethod
    def initialize_piece_dict() -> list:
        """
        Creates a list containing dictionaries of piece counts for each player [white,black]
        :return: list of dicts
        """

        white_dict = {}
        black_dict = {}

        for piece in s.valid_pieces:
            white_dict[piece] = 0
            black_dict[piece] = 0

        return [white_dict, black_dict]

    def get_square_info(self, square: int) -> tuple:
        color = self.get_square_color(square)
        piece = self.get_square_piece(square)
        return color, piece

    def get_square_color(self, square: int, none_check=False) -> str:
        """
        Gets color of piece based on board dict index
        :param square: square index
        :param none_check: flag if a non valid (empty or off board) piece should be returned as None
        :return: w/b or None if empty square/outside of game board
        """
        color = self.board[square][0]
        return color if color in s.valid_colors else None if none_check else color

    def get_square_piece(self, square: int, none_check=False) -> str:
        """
        Gets piece based on board dict index
        :param square: square index
        :param none_check: flag if a non valid (empty or off board) piece should be returned as None
        :return: w/b or None if empty square/outside of game board
        :return:
        """
        piece = self.board[square][1]
        return piece if piece in s.valid_pieces else None if none_check else piece

    def init_piece_columns(self):
        """
        Populates these random empty lists, such that the square column is added to a list for each color/
        piece of interest
        :return: None
        """
        # FIXME - hate lots of this lol! # note - don't think this is super important for now though
        for square in self.board:
            piece_type, color = self.get_square_piece(square), self.get_square_color(square)
            # FIXME - for now just going to continue iterating over every cell, but in future would like to track
            #       - the pieces location (wasted loops on non pieces may add up? probably not but will see!)
            if piece_type in c.column_pieces:
                # FIXME - surely generalize such that you can track any column?
                #       - this makes me think that this is very specific evaluation helper data
                if piece_type == 'R':
                    if color == 'w':
                        # Fixme - don't like how the individual colors are referenced here with 0/1 implied
                        self.rook_columns_list[0].append(square % 10)
                    elif color == 'b':
                        self.rook_columns_list[1].append(square % 10)
                elif piece_type == 'p':
                    if color == 'w':
                        self.pawn_columns_list[0].append(square % 10)
                    elif color == 'b':
                        self.pawn_columns_list[1].append(square % 10)

    def game_constant_A(self):
        """
        Constant to be used in evaluating
        :return: A value
        """
        example = min(self.full_move, 50)/50
        return example

    def game_constant_B(self):
        """
        Constant to be used in evaluating
        :return: B value
        """
        return 1

    def update_game_constants(self):
        """
        Calls the game constant function and sets the value within game_constant dict
        """
        for constant, (value, func) in self.game_constants.items():
            self.game_constants[constant][0] = func()




#test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
#test_fen = 'r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1'  # kings and rooks
#test_fen = '4k2r/8/8/8/8/8/r7/R1K5 w - - 0 1'

"""
test_fen = '8/8/8/2p5/8/pN6/8/Q1Rp4 w - - 0 1'
test_instance = GameInstance(starting_fen=test_fen)


# Randomly making moves to test
while 1:
    test_instance.get_all_possible_moves()
    move = random.choice(test_instance.possible_moves)
    test_instance.make_move(move)
#print('exiting')
"""