import fen_logic as fl
import fen_settings as s


class GameInstance:
    def __init__(self, starting_fen):

        self.starting_fen = starting_fen
        self.board, self.castling_rights, self.en_passant_square, self.half_move, self.full_move, self.is_whites_turn =\
            fl.decode_fen(self.starting_fen)

        self.piece_dict = self.initialize_piece_dict()
        self.initialize_piece_count_dict()
        print('wait')

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

    def get_square_color(self):
        return None

    def get_square_piece(self):
        return None


if __name__ == '__main__':
    test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    test_instance = GameInstance(starting_fen=test_fen)
    print('exiting')
