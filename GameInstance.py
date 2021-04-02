import fen_logic as fl
import fen_settings as s
import config as c
import random
import time
from numba import jit
import chess

class GameInstance:
    def __init__(self, starting_fen):

        self.starting_fen = starting_fen
        self.board, self.castling_rights, self.en_passant_square, self.half_move, self.full_move, self.is_whites_turn = \
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

        self.move_log = []

        self.get_all_possible_moves()

    def get_legal_moves(self):
        self.get_all_possible_moves()
        return self.possible_moves

    #@profile
    def make_move(self, move):

        # unpacking FIXME - don't like how unclear this is
        [start_square, end_square, move_type, delta_eval] = move

        piece_moved = self.board[start_square]
        piece_captured = self.board[end_square]

        piece_color, piece_type = self.get_square_info(start_square)  # start square contents

        if move_type != 'no':
            if move_type == 'two_square_pawn':
                self.board[end_square] = piece_moved
                self.board[start_square] = '--'
                self.en_passant_square = int(start_square + (end_square - start_square) / 2)

            if move_type == 'enpassant':
                # FIXME - small graphical bug - but no biggie

                taken_piece_square = end_square + 10 if start_square - end_square > 0 else end_square - 10
                self.board[taken_piece_square] = '--'
                # self.board[self.en_passant_square] = '--'
                self.en_passant_square = None  # Fixme - dont want to do this every move
                self.board[end_square] = piece_moved
                self.board[start_square] = '--'

            if move_type == 'Qpromotion':
                # self.board[self.en_passant_square] = '--'
                self.board[end_square] = "{}Q".format(piece_color)
                self.board[start_square] = '--'
                self.en_passant_square = None  # Fixme - dont want to do this every move

            if piece_type == 'K':
                # Update king positions
                self.board[end_square] = piece_moved
                self.board[start_square] = '--'
                self.en_passant_square = None
                self.king_location[piece_color] = end_square

        else:
            self.board[end_square] = piece_moved
            self.board[start_square] = '--'
            self.en_passant_square = None

        self.move_log.append([move, piece_moved, piece_captured, self.en_passant_square])

        self.turn_over()

    #@profile
    def unmake_move(self):

        self.turn_over()  # switches turn

        # Loading previous move and unpacking
        previous_move = self.move_log.pop()
        [start_square, end_square, move_type, delta_eval] = previous_move[0]
        piece_moved = previous_move[1]
        piece_captured = previous_move[2]
        enpassant_square = previous_move[3]

        piece_color, piece_type = self.get_square_info(end_square)  # end square contents

        # Update board
        self.board[start_square] = piece_moved
        self.board[end_square] = piece_captured

        # piece specific move updates
        if piece_moved == 'wK':
            self.king_location['w'] = start_square
        elif piece_moved == 'bK':
            self.king_location['b'] = start_square

        if move_type != 'no':
            # Non "normal" moves updates
            if move_type == 'Qpromotion':
                # Instead undo back to a pawn
                self.board[start_square] = '{}p'.format(piece_color)

            if move_type == 'enpassant':
                self.board[end_square] = '--'
                forward_dir = 10 if piece_color == 'b' else -10
                enemy = 'w' if piece_color == 'b' else 'b'
                self.board[end_square-forward_dir] = '{}w'.format(enemy)
                #TODO - validate this!


    def turn_over(self):
        self.is_whites_turn = not self.is_whites_turn
        self.turn = self.update_turn()

    def update_turn(self):
        return 'w' if self.is_whites_turn else 'b'

    #@profile
    def get_all_legal_moves(self):

        king_pos = self.king_location['w'] if self.is_whites_turn else self.king_location['b']
        self.is_in_check, self.pins, self.checks = self.check_pins_and_checks(king_pos)
        self.get_all_possible_moves()
        moves = self.possible_moves

        enemy_color = 'b' if self.is_whites_turn else 'w'
        color = 'w' if self.is_whites_turn else 'b'

        if self.is_in_check:
            if len(self.checks) == 1:
                # Check from a singular piece - potential to block or take it
                moves = self.get_all_possible_moves()

                check_info = self.checks[0]
                checking_piece_square = check_info[0]
                checking_dir = check_info[1]

                checking_piece_c, checking_piece = self.get_square_info(checking_piece_square)  # square contents

                squares_to_stop_check = []
                if checking_piece == 'N':
                    squares_to_stop_check.append(checking_piece_square)
                else:
                    for step in range(1, 8):
                        square_f = king_pos + checking_dir * step
                        color_f, piece_f = self.get_square_info(square_f)  # end square contents
                        if piece_f == '-' or piece_f == checking_piece:
                            squares_to_stop_check.append(square_f)

                        if piece_f == checking_piece:
                            break

                self.get_all_possible_moves()
                moves = self.possible_moves
                moves = [move for move in moves if (move[1] in squares_to_stop_check or 'K' in move[2])]

                #print('downsampled for moves that remove check!')
                #print(squares_to_stop_check)
                #print(moves)

            else:
                # 2+ checks - only able to move the king # TODO - confirm this is true? fairly sure it is
                moves = []
                self.get_king_moves(king_pos, moves)
        else:
            # All moves are valid (no checks) # TODO - pins still need to be added
            pass
            #self.get_all_possible_moves()
            #moves = self.possible_moves

        #moves = [move for move in moves if (move[0] not in self.pins.keys() or (len(self.pins[move[0]]) == 1 and (self.pins[move[0]][1] % abs(move[1]-move[0]) == 0)))]  # FIXME - can actually take the piece causing the pin! (so long as its the sole piece pinning it)

        filtered_moves = []
        for move in moves:
            if move[0] not in self.pins.keys():
                filtered_moves.append(move)
            elif len(self.pins[move[0]]) == 1:
                # FIXME - dont think multiple pins can be occouring on the same piece??
                dir = self.pins[move[0]][0]
                op_dir = -dir
                delta_move = move[1] - move[0]
                if delta_move % dir == 0 or delta_move % op_dir == 0:
                    filtered_moves.append(move)

        return filtered_moves

    def check_pins_and_checks(self, square):

        pin_list = {}
        check_list = []
        is_in_check = False

        enemy_color = 'b' if self.is_whites_turn else 'w'
        color = 'w' if self.is_whites_turn else 'b'
        pawn_direction = -1 if self.is_whites_turn else 1

        pin_dir = {'R': (s.linear_dirs, 8),
                      'B': (s.diagonal_dirs, 8),
                      'Q': (s.linear_dirs + s.diagonal_dirs, 8),
                      'p': (s.diagonal_dirs * pawn_direction, 1),
                      'N': ([], 1),
                      'K': ([], 1)}  # Fixme - why is N/K in here!

        for direction in s.linear_dirs + s.diagonal_dirs:

            possible_pin = False

            for step in range(1, 8):
                square_f = square + direction * step
                color_f, piece_f = self.get_square_info(square_f)  # end square contents

                if piece_f != 'F':  # on the board

                    if color_f == color and not possible_pin:
                        # first piece in direction (own)
                        possible_pin = (square_f, direction)

                    elif color_f == color and possible_pin:
                        # second piece in direction (own) - no pin
                        break

                    elif color_f == enemy_color and possible_pin:
                        # second piece in direction (enemy) - possible pin
                        if direction in pin_dir[piece_f][0] and step <= pin_dir[piece_f][1]:

                            # check if piece can deliver a pin
                            if possible_pin[0] in pin_list:
                                pin_list[possible_pin[0]].append(direction)
                            else:
                                pin_list[possible_pin[0]] = [direction]

                        break

                    elif color_f == enemy_color and not possible_pin:
                        # first piece in direction (enemy) - possible check
                        if direction in pin_dir[piece_f][0] and step <= pin_dir[piece_f][1]:
                            # check if piece can deliver a check
                            check_list.append((square_f, direction))
                            is_in_check = True
                        break
                else:
                    # Off the board, stop checking in that dir
                    break

        for direction in s.knight_moves:
            square_f = square + direction
            color_f, piece_f = self.get_square_info(square_f)  # end square contents
            if color_f == enemy_color and piece_f == 'N':
                check_list.append((square_f, direction))
                is_in_check = True

        #if is_in_check:
            #print('CHECK!')

        return is_in_check, pin_list, check_list

    def check_check(self, square):
        # Checks if the square is valid for the king to move to
        enemy_color = 'b' if self.is_whites_turn else 'w'
        color = 'w' if self.is_whites_turn else 'b'
        pawn_direction = -1 if self.is_whites_turn else 1

        attack_dir = {'R': (s.linear_dirs, 8),
                      'B': (s.diagonal_dirs, 8),
                      'Q': (s.linear_dirs + s.diagonal_dirs, 8),
                      'p': (s.diagonal_dirs * pawn_direction, 1),
                      'N': ([], 1),
                      'K': (s.diagonal_dirs + s.linear_dirs, 1)}  # Fixme - why is N/K in here!

        for direction in s.linear_dirs + s.diagonal_dirs:
            for step in range(1, 9):
                square_f = square + direction * step
                color_f, piece_f = self.get_square_info(square_f)  # end square contents

                if color_f == color or piece_f == 'F':
                    if piece_f != 'K':  # Hiding behind itself bug
                        break
                elif color_f == enemy_color:
                    if direction in attack_dir[piece_f][0] and step <= attack_dir[piece_f][1]:
                        #print('square {} is checked'.format(square))

                        return True
                    else:
                        break

        for direction in s.knight_moves:
            square_f = square + direction
            color_f, piece_f = self.get_square_info(square_f)  # end square contents
            if color_f == enemy_color and piece_f == 'N':
                return True

        #print('no checks for {}'.format(square))
        return False

    #@profile
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
    #@profile
    def get_pawn_moves(self, square, moves):

        enemy_color = 'b' if self.is_whites_turn else 'w'
        #color = 'w' if self.is_whites_turn else 'b'

        pawn_start_cords = s.white_pawn_start if self.is_whites_turn else s.black_pawn_start
        enemy_pawn_start_cords = s.black_pawn_start if self.is_whites_turn else s.white_pawn_start
        pawn_en_passant_cords = s.white_pawn_en_passant_cords if self.is_whites_turn else s.black_pawn_en_passant_cords
        pawn_end_cords = s.white_pawn_end if self.is_whites_turn else s.black_pawn_end
        pawn_direction = -1 if self.is_whites_turn else 1

        #pawn_start_cords = s.white_pawn_start if self.is_whites_turn else s.black_pawn_start
        #pawn_en_passant_cords = [cord + 10 * pawn_direction for cord in pawn_start_cords]
        #pawn_end_cords = [cord + 10 * pawn_direction for cord in enemy_pawn_start_cords]
        #color_s, piece_s = self.get_square_info(square)  # start square contents

        piece_s = self.board[square][1]

        # Moving forward
        available_steps = [1, 2] if square in pawn_start_cords else [1]
        for step_size in available_steps:
            square_f = square + s.up * step_size * pawn_direction
            #color_f, piece_f = self.get_square_info(square_f)  # end square contents
            piece_f = self.board[square_f][1]

            if piece_f == '-':  # empty
                if square_f in pawn_end_cords:
                    piece_e = "Q"
                    piece_increase = (
                            s.piece_value_mid_game[piece_e][square_f] - s.piece_value_mid_game[piece_s][square])
                    moves.append((square, square_f, 'Qpromotion', piece_increase))
                else:
                    piece_increase = (
                            s.piece_value_mid_game[piece_s][square_f] - s.piece_value_mid_game[piece_s][square])
                    move_type = 'two_square_pawn' if step_size == 2 else 'no'
                    moves.append((square, square_f, move_type, piece_increase))
            else:
                # Don't check 2 if 1 is blocked
                break

        # Taking on diagonal + enpassantg
        available_steps = s.diagonals
        for step in available_steps:
            square_f = square + step * pawn_direction
            color_f, piece_f = self.board[square_f][0], self.board[square_f][1]  # end square contents
            if color_f == enemy_color:
                if square_f in pawn_end_cords:
                    # Promotion
                    piece_e = "Q"
                    piece_increase = (
                            s.piece_value_mid_game[piece_e][square_f] - s.piece_value_mid_game[piece_s][square])
                    moves.append((square, square_f, 'Qpromotion', piece_increase + s.mvv_lva_values[piece_f]))

                else:
                    piece_increase = (
                            s.piece_value_mid_game[piece_s][square_f] - s.piece_value_mid_game[piece_s][square])
                    moves.append((square, square_f, 'no', piece_increase + s.mvv_lva_values[piece_f]))

            elif square_f == self.en_passant_square and square_f not in pawn_en_passant_cords:
                #print('enpassant we we!')
                piece_increase = (s.piece_value_mid_game[piece_s][square_f] - s.piece_value_mid_game[piece_s][square])
                moves.append((square, square_f, 'enpassant', piece_increase + s.mvv_lva_values[piece_f]))
            # print(square_f, self.en_passant_square)
    #@profile
    def get_knight_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.knight_moves:
            end_square = square + direction  # moving in the direction one step
            color_s, piece_s = self.get_square_info(square)  # start square conents
            color_e, piece_e = self.get_square_info(end_square)  # end square contents

            if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                # TODO - implement pin check logic
                # if not piece_pinned or pin_direction in (d, -d):  #

                # note - calculating the increase in piece value based on move and game phase
                # TODO - increase this such that there are multiple tables extrapolated between based on phase
                piece_increase = (s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                # note - start/end sqaure - no (TODO  what this this)
                # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                # note - these are not needed for knight as not a sliding piece
                # note - if the end_square houses a enemy piece - stop checking in that direction.
                # if color_e == enemy_color:
                #    break  # break out of that direction
            # else:
            #    break
    #@profile
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
                    # if not piece_pinned or pin_direction in (d, -d):  #

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
    #@profile
    def get_rook_moves(self, square, moves):
        # note - tried to make this faster by cutting unused calls/leaving them as late as possible!


        enemy_color = 'b' if self.is_whites_turn else 'w'
        piece_s = 'R'
        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        for direction in s.linear_dirs:
            for i in range(1, 8):
                end_square = square + direction * i  # moving in the direction one step

                #color_s, piece_s = self.board[square][0], self.board[square][1]  # start square contents
                #color_e, piece_e = self.board[end_square][0], self.board[end_square][1]  # end square contents

                color_e = self.board[end_square][0]
                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    # if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (
                            s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[self.board[end_square][1]]))

                    # note - if the end_square houses a enemy piece - stop checking in that direction.
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break
    #@profile
    def get_queen_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        color_s, piece_s = self.get_square_info(square)  # start square contents

        for direction in s.diagonal_dirs + s.linear_dirs:  # FIXME - this shouldn't be in the loop for rook, bishop, queen
            for i in range(1, 8):
                end_square = square + direction * i  # moving in the direction one step
                color_e, piece_e = self.get_square_info(end_square)  # end square contents

                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    # if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (
                            s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    moves.append((square, end_square, 'no', piece_increase + s.mvv_lva_values[piece_e]))

                    # note - if the end_square houses a enemy piece - stop checking in that direction.
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break
    #@profile

    def get_king_moves(self, square, moves):
        enemy_color = 'b' if self.is_whites_turn else 'w'
        color = self.turn

        # TODO continue back here tomorrow :)
        # note - currently not doing any pin checks! pseudo legal move generator.
        color_s, piece_s = self.get_square_info(square)  # start square contents



        # note - come back to this in the morning! <3 
        """
        # Castling:
        # Can't castle if in check, if square between K or R is under attack, or if castling rights are broken
        if not self.is_in_check:
            king_castle = 'K' if self.is_whites_turn else 'k'
            queen_castle = 'Q' if self.is_whites_turn else 'q'

            # Castle King side
            if king_castle in self.castling_rights and all(x == '--' for x in (self.board[square + 1], self.board[square + 2])):

                # Check if squares are in check or not
                is_in_check_1 = self.check_for_checks(square + 1)
                is_in_check_2 = self.check_for_checks(square + 2)

                if not (is_in_check_1 or is_in_check_2):
                    moves.append((square, square + 2, 'ck', 40))

            # Castle Queen side
            if queen_castle in self.castling_rights and all(x == '--' for x in (self.board[square - 1], self.board[square - 2], self.board[square - 3])):

                # Check if squares are in check or not, king doesn't pass the knight square on queenside castle so no use in checking that square
                is_in_check_1 = self.check_for_checks(square - 1)
                is_in_check_2 = self.check_for_checks(square - 2)

                if not (is_in_check_1 or is_in_check_2):
                    moves.append((square, square - 2, 'cq', 40))

        """







        for direction in s.diagonal_dirs + s.linear_dirs:  # FIXME - this shouldn't be in the loop for rook, bishop, queen
            for i in range(1, 2):
                end_square = square + direction * i  # moving in the direction one step
                color_e, piece_e = self.get_square_info(end_square)  # end square contents

                if color_e in [enemy_color, '-']:  # seeing if enemy piece at final square or empty (valid sqare check)
                    # TODO - implement pin check logic
                    # if not piece_pinned or pin_direction in (d, -d):  #

                    # note - calculating the increase in piece value based on move and game phase
                    # TODO - increase this such that there are multiple tables extrapolated between based on phase
                    piece_increase = (
                            s.piece_value_mid_game[piece_s][end_square] - s.piece_value_mid_game[piece_s][square])

                    # note - start/end sqaure - no (TODO  what this this)
                    # note -  delta of evaluation (based on the above tables + the taken piece (end square value)
                    if not self.check_check(end_square):
                        moves.append((square, end_square, '{}K'.format(color_s), piece_increase + s.mvv_lva_values[piece_e]))
                        #if self.turn == 'b':
                            #print('{} valid king square'.format(end_square))
                    # note - if the end_square houses a enemy piece - stop checking in that direction???? #FIXME
                    if color_e == enemy_color:
                        break  # break out of that direction
                else:
                    break

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

    #@jit
    def get_square_info(self, square):
        return self.board[square][0], self.board[square][1]
        #color = self.get_square_color(square)
        #piece = self.get_square_piece(square)
        #return color, piece

    #@profile
    def get_square_color(self, square: int, none_check=False) -> str:
        """
        Gets color of piece based on board dict index
        :param square: square index
        :param none_check: flag if a non valid (empty or off board) piece should be returned as None
        :return: w/b or None if empty square/outside of game board
        """
        return self.board[square][0]
        color = self.board[square][0]
        return color if color in s.valid_colors else None if none_check else color
    #@profile
    def get_square_piece(self, square: int, none_check=False) -> str:
        """
        Gets piece based on board dict index
        :param square: square index
        :param none_check: flag if a non valid (empty or off board) piece should be returned as None
        :return: w/b or None if empty square/outside of game board
        :return:
        """
        return self.board[square][1]
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
        example = min(self.full_move, 50) / 50
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


# test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
# test_fen = 'r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1'  # kings and rooks
# test_fen = '4k2r/8/8/8/8/8/r7/R1K5 w - - 0 1'


def move_counter(game, depth):
    if depth == 0:
        return 1

    else:
        moves = game.get_all_legal_moves()
        count = 0

        for move in moves:
            game.make_move(move)
            count += move_counter(game, depth-1)
            game.unmake_move()

    return count



test_fen = '1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - 0 1'
test_instance = GameInstance(starting_fen=test_fen)

t0 = time.time()
move_count = move_counter(test_instance, depth=4)
t1 = time.time()
my_time = t1-t0
print("{} boards found".format(move_count))
print("{} secs".format(t1-t0))
print("{} boards/sec".format(move_count/(t1-t0)))


def move_counter2(board, depth):
    if depth == 0:
        return 1

    else:
        moves = board.legal_moves
        count = 0

        for move in moves:
            board.push(move)
            count += move_counter2(board, depth-1)
            board.pop()

    return count




print('starting pychess test')
board = chess.Board()
t0 = time.time()
move_count = move_counter2(board, depth=4)
t1 = time.time()
print("{} boards found".format(move_count))
print("{} secs".format(t1-t0))
print("{} boards/sec".format(move_count/(t1-t0)))
their_time = t1-t0

print("{0:.2f}% speed up!".format(100*((their_time/my_time)-1)))

"""
while 1:
    test_instance.get_all_possible_moves()
    move = random.choice(test_instance.possible_moves)
    test_instance.make_move(move)
#print('exiting')
"""