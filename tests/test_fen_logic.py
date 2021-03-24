from fen_logic import decode_fen


def test_decode_fen():
    test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    actual = decode_fen(test_fen)
    expected = {}  # TODO - fill this out with the exptected dictionary
    print(len(expected))
    assert actual == expected


def test_decode_fen2():
    test_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    actual = decode_fen(test_fen)
    expected = {}  # TODO - fill this out with the exptected dictionary
    print(len(expected))
    assert actual == expected