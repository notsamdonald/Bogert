import tkinter as tk
from tkinter import *
import random
from PIL import Image, ImageTk
from AlphaBetaPruning import *
import cProfile

import chess
import chess.engine
import chess.pgn

global canvasSize
canvasSize = 1

game = chess.pgn.Game()
game.headers["Event"] = "Example"


class TkFrame(Frame):
    # main Tk frame

    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RAISED)
        self.parent = parent
        self.img = {}
        self.initUI()

    def initUI(self):
        self.parent.title("Raven Chess GUI 0.10")
        self.parent.minsize(687, 505)
        self.pack(fill=BOTH, expand=YES)


def drawPieces():
    global board
    global boardCanvas
    global canvasSize
    global app
    global flipped
    global count
    count = 0
    app.img = {}
    # dspboard = list(board)
    # if flipped: dspboard = reversed(board)
    # if boardHistoryPos != (len(boardHistory) - 1) and boardHistory != []:
    #	dspboard = list(boardHistory[boardHistoryPos])
    #	if flipped: dspboard = reversed(dspboard)
    for i in range(0, 64):
        c = 63 - i
        # xTile goes from 0 to 7 (files)
        # yTile goes from 0 to 7 (ranks)
        xTile = ((7 - c) % 8)  # every 8th byte is a new row
        yTile = int(c / 8)  # each column is the nth byte in a row
        squareSize = int(canvasSize / 8)
        if squareSize < 1: squareSize = 1
        xDrawPos = (xTile * squareSize) - 3
        yDrawPos = (yTile * squareSize) - 3
        if flipped:
            xDrawPos = ((7 - xTile) * squareSize) - 3
            yDrawPos = ((7 - yTile) * squareSize) - 3

        mytext = str(i)
        piece = str(board.piece_at(i))

        pieceFile = ''

        if piece == 'R': pieceFile = 'pieces\WR.png'  # white rook
        if (piece == 'N'): pieceFile = 'pieces\WN.png'  # white knight
        if (piece == 'B'): pieceFile = 'pieces\WB.png'  # white bishop
        if (piece == 'Q'): pieceFile = 'pieces\WQ.png'  # white queen
        if (piece == 'K'): pieceFile = 'pieces\WK.png'  # white king
        if (piece == 'P'): pieceFile = 'pieces\WP.png'  # white pawn

        if (piece == 'r'): pieceFile = 'pieces\BR.png'  # black rook
        if (piece == 'n'): pieceFile = 'pieces\BN.png'  # black knight
        if (piece == 'b'): pieceFile = 'pieces\BB.png'  # black bishop
        if (piece == 'q'): pieceFile = 'pieces\BQ.png'  # black queen
        if (piece == 'k'): pieceFile = 'pieces\BK.png'  # black king
        if (piece == 'p'): pieceFile = 'pieces\BP.png'  # black pawn

        if (pieceFile != ''):
            img = Image.open(pieceFile)
            img = img.resize((squareSize - 0, squareSize - 0), Image.ANTIALIAS)
            app.img[count] = ImageTk.PhotoImage(img)
            boardCanvas.create_image(xDrawPos + 3, yDrawPos + 3, image=app.img[count], anchor=NW)

        count += 1


def appresize(event):
    global boardCanvas
    global canvasSize
    global app
    global root
    global boardImg

    boardCanvas.pack(expand=YES)
    # boardCanvas.config(width=30, height=30,bg="black")
    # boardCanvas.pack(expand=NO)
    # print app.winfo_height()
    appheight = app.winfo_height()
    appwidth = app.winfo_width()
    biggestDim = "height"
    canvasSize = appwidth - 202
    if appwidth > appheight:
        biggestDim = "width"
        canvasSize = appheight - 25
    if appwidth < (canvasSize + 202):
        canvasSize = appwidth - 202

    canvasSize = (int(canvasSize / 8) * 8)
    h = canvasSize
    w = canvasSize
    # boardImg.zoom(scalew, scaleh)
    boardCanvas.place(x=00, y=0, w=w, h=h)
    gameStateLabel.place(x=0, y=h + 1, w=300, h=20)
    drawBoard()
    drawPieces()
    root.update()


def drawBoard():
    global count
    global boardCanvas
    global canvasSize
    global colLight, colDark
    global app
    global boardImg
    global scalew, scaleh
    count = 0
    board = ''
    # img = Image.Open(file='board.PNG')
    img = Image.open("board.PNG")
    img = img.resize((canvasSize, canvasSize), Image.ANTIALIAS)
    boardImg = ImageTk.PhotoImage(img)
    # boardImg.config(file='board.PNG')
    # boardImg = PhotoImage(file='board.PNG').zoom(320,320)
    # boardImg.width = scalew
    # boardImg.height = scaleh
    # print dir(boardImg)
    boardCanvas.delete("all")
    boardCanvas.create_image(3, 3, image=boardImg, anchor=NW)


def convertXYtoBoardIndex(x, y):
    global flipped
    global canvasSize

    squareSize = canvasSize / 8
    # Converts cursor X, Y position to board array X, Y position
    returnX = int(x / squareSize)
    returnY = int(y / squareSize)
    if flipped:
        returnX = int((canvasSize - x) / squareSize)
        returnY = int((canvasSize - y) / squareSize)
    return (returnX, returnY)


def convertBoardIndextoXY(x, y):
    global flipped
    global canvasSize

    squareSize = canvasSize / 8
    # Converts board index X, Y to tile draw position X, Y
    returnX = x * squareSize
    returnY = y * squareSize
    if flipped:
        returnX = int((7 - x) * squareSize)
        returnY = int((7 - y) * squareSize)
    return (returnX, returnY)


def islower(c):
    if c >= 'a' and c <= 'z': return True
    return False


def isupper(c):
    if c >= 'A' and c <= 'Z': return True
    return False


def canvasClick(event):
    global clickDragging
    global canvasSize

    global ClickStartScrPos
    global clickStartPiece
    global clickStartBoardIndex
    global lastTileXIndex, lastTileYIndex
    global clickStartSquare
    global board
    if ((board.turn and p1 == "Human") or (not board.turn and p2 == "Human")):
        # human to move

        squareSize = canvasSize / 8
        mouseX = event.x
        mouseY = event.y

        # convert mouseX, mouseY to board array indices
        (tileXIndex, tileYIndex) = convertXYtoBoardIndex(mouseX, mouseY)
        # convert board indices to screen X Y position of tiles
        (tileScrX, tileScrY) = convertBoardIndextoXY(tileXIndex, tileYIndex)

        boardIndex = tileYIndex * 8 + tileXIndex
        boardIndex = 63 - boardIndex
        boardIndexX = 7 - (boardIndex % 8)
        boardIndexY = int(boardIndex / 8)
        boardIndex = boardIndexY * 8 + boardIndexX
        piece = board.piece_at(boardIndex)

        if (piece == None): return
        if ((board.turn and islower(str(piece))) or (not board.turn and isupper(str(piece)))): return

        # draw green square over tile
        # boardCanvas.draw.rect(pygScreen, (0,255,0), (tileScrX + 2, tileScrY + 2, 57, 57), 4)
        boardCanvas.create_rectangle(tileScrX + 3, tileScrY + 3, (tileScrX + squareSize - 2),
                                     (tileScrY + squareSize - 2), outline="#00FF00",
                                     width=6)
        clickDragging = True
        clickStartScrPos = (tileScrX, tileScrY)  # store top left screen X, Y for tile position
        clickStartBoardIndex = (tileXIndex, tileYIndex)
        clickStartPiece = piece
        lastTileXIndex = tileXIndex
        lastTileYIndex = tileYIndex
        clickStartSquare = boardIndex


def canvasMotion(event):
    global lastTileScrX
    global lastTileScrY
    global lastTileXIndex
    global lastTileYIndex
    global canvasSize
    global clickStartBoardIndex
    global clickStartSquare
    global clickEndSquare

    if not clickDragging: return
    squareSize = canvasSize / 8
    mouseX = event.x
    mouseY = event.y
    if (mouseX > canvasSize or mouseX < 0 or mouseY > canvasSize or mouseY < 0): return
    # convert mouseX, mouseY to board array indices
    (tileXIndex, tileYIndex) = convertXYtoBoardIndex(mouseX, mouseY)
    # convert board indices to screen X Y position of tiles
    (tileScrX, tileScrY) = convertBoardIndextoXY(tileXIndex, tileYIndex)

    # clickStartBoardIndex = (tileXIndex, tileYIndex)
    # calculate boardIndex = board[] square index
    boardIndex = tileYIndex * 8 + tileXIndex
    boardIndex = 63 - boardIndex
    boardIndexX = 7 - (boardIndex % 8)
    boardIndexY = int(boardIndex / 8)
    boardIndex = boardIndexY * 8 + boardIndexX
    clickEndSquare = boardIndex
    move = chess.Move(from_square=clickStartSquare, to_square=boardIndex)
    islegal = False
    for legalmove in board.legal_moves:
        if str(move) == str(legalmove): islegal = True
    if islegal:
        # draw green square over moused over square
        boardCanvas.create_rectangle(tileScrX + 3, tileScrY + 3, (tileScrX + (squareSize - 2)),
                                     (tileScrY + (squareSize - 2)),
                                     outline="#00FF00", width=6)
        if ((lastTileXIndex != tileXIndex) or (lastTileYIndex != tileYIndex)):  # user mouses to a new square
            if (clickStartBoardIndex != (lastTileXIndex, lastTileYIndex)):  # don't redraw if it's the start square
                redrawTile(lastTileXIndex, lastTileYIndex)  # redraw over last square (to remove green rect)

        lastTileXIndex = tileXIndex
        lastTileYIndex = tileYIndex


def canvasRelease(event):
    global clickDragging
    global board, root
    global clickStartSquare
    global p1, p2
    global gameStateVar
    global clickEndSquare

    if (clickDragging == False):
        return

    clickDragging = False
    mouseX = event.x
    mouseY = event.y

    # convert mouseX, mouseY to board array indices
    (tileXIndex, tileYIndex) = convertXYtoBoardIndex(mouseX, mouseY)
    # convert board indices to X Y position of tiles
    # (tileScrX, tileScrY) = convertBoardIndextoXY(tileXindex, tileYindex)
    # startSquare = (clickStartBoardIndex[0], clickStartBoardIndex[1])
    # endSquare = (tileXindex, tileYindex)

    endSquare = clickEndSquare
    # startSquare = clickStartSquare[1] * 8 + clickStartSquare[0]
    # startSquare = 63 - startSquare
    startSquare = clickStartSquare

    move = chess.Move(from_square=startSquare, to_square=endSquare)
    islegal = False
    for legalmove in board.legal_moves:
        if str(move) == str(legalmove): islegal = True
    if islegal:
        board.push(move)
        if (board.turn):
            gameStateVar.set("White to move.")
        else:
            gameStateVar.set("Black to move.")

    drawBoard()
    drawPieces()
    root.update()
    legalmoves = board.legal_moves
    count = 0
    for x in legalmoves:
        count += 1
    if (count == 0):
        gameStateVar.set("End of game.")
        root.update()
        return
    if (board.turn and p1 != "Human"):
        getAIMove(turn='White')
    elif (not board.turn and p2 != "Human"):
        getAIMove(turn='Black')


def AI_1(board):
    '"Beep boop I am awful at Chess" - AI_1'
    'de'
    move_type = random.choice([1, 2, 3])
    if move_type > 1:
        move = minimaxRoot(random.choice([2, 3]), board, True)
    else:
        move = random.choice(list(board.legal_moves))

    return move


def AI_2(board, white_move=False):
    '"Beep boop I am slightly better at Chess... hopefully" - AI_2'
    'do'
    # move = random.choice(list(board.legal_moves))
    move = minimaxRoot(2, board, board.turn)
    # TODO: Add some noise or randomness into the move selection (normalize it beforehand by ?)
    return move


#@profile
def AI_3(board):
    'mo'

    move = minimaxRoot(4, board, board.turn, square_bonus=True)

    return move


def AI_4():
    'me'
    return None


def AI_5():
    'la'
    return None


def getAIMove(turn):
    global board
    global root
    global canvasSize
    global gameStateVar
    global pvmove

    lastpvmovestr = ""
    # if (p1 == "AI" and board.turn): engine = engine1
    # elif (p2 == "AI" and not board.turn): engine = engine2
    if False:
        with engine.analysis(board, chess.engine.Limit(time=(1.5))) as analysis:
            for info in analysis:
                if (info.get("pv") != None):
                    pvmove = info.get("pv")[0]
                    pvmovestr = str(pvmove)
                    if lastpvmovestr != pvmovestr:
                        startfile = ord(pvmovestr[0]) - 97
                        startrank = ord(pvmovestr[1]) - 49
                        endfile = ord(pvmovestr[2]) - 97
                        endrank = ord(pvmovestr[3]) - 49
                        startrank = 7 - startrank
                        endrank = 7 - endrank
                        squareSize = canvasSize / 8
                        (startScrX, startScrY) = convertBoardIndextoXY(startfile, startrank)
                        (endScrX, endScrY) = convertBoardIndextoXY(endfile, endrank)
                        drawBoard()
                        drawPieces()
                        boardCanvas.create_rectangle(startScrX + 3, startScrY + 3, (startScrX + squareSize - 2),
                                                     (startScrY + squareSize - 2), outline="#0000FF",
                                                     width=6)
                        boardCanvas.create_rectangle(endScrX + 3, endScrY + 3, (endScrX + squareSize - 2),
                                                     (endScrY + squareSize - 2), outline="#0000FF",
                                                     width=6)
                        root.update()
                    lastpvmovestr = pvmovestr
    # pvmove = analysis.info['pv'][0]

    if turn == 'White':
        move = AI_3(board)
    else:
        move = AI_3(board)

    if move == 'No' or move is None:
        gameStateVar.set("End of game.")
        root.update()
        gameinprogress = False
    else:
        print(move)
        board.push_uci(str(move))
        drawBoard()
        drawPieces()

    legalmoves = board.legal_moves
    count = 0

    for x in legalmoves:
        count += 1
    # print(count, legalmoves)
    if (count == 0):
        gameStateVar.set("End of game.")
        root.update()
        gameinprogress = False
        print('no legal')

    else:
        if (board.turn):
            gameStateVar.set("White to move.")
        else:
            gameStateVar.set("Black to move.")
        root.update()
        if (p1 == "AI" and board.turn):
            getAIMove(turn='white')
        elif (p2 == "AI" and not board.turn):
            getAIMove(turn='black')


def redrawTile(x, y):
    global count
    global board
    global flipped
    global canvasSize
    count = 0
    colLight = (128, 128, 128)
    colDark = (196, 196, 196)
    colLight = '#%02x%02x%02x' % colLight
    colDark = '#%02x%02x%02x' % colDark

    squareSize = canvasSize / 8
    # redraws a tile with its piece
    boardIndex = y * 8 + x
    boardIndex = 63 - boardIndex
    boardIndexX = 7 - (boardIndex % 8)
    boardIndexY = int(boardIndex / 8)
    boardIndex = boardIndexY * 8 + boardIndexX
    i = x
    j = y
    xpos = (i * squareSize) - 3
    ypos = (j * squareSize) - 3  # each tile is 60x60 px
    if flipped:
        xpos = ((7 - i) * squareSize)
        ypos = ((7 - j) * squareSize)
    col = colLight
    if (((i + j) % 2) == 0): col = colDark  # alternate tiles are dark
    # redraw tile
    drawEndX = (xpos + squareSize)
    drawEndY = (ypos + squareSize)
    if flipped:
        drawEndX = ((7 - xpos) + squareSize)
        drawEndY = ((7 - ypos) + squareSize)

    tempDrawDir = 1
    if (not board.turn) and (flipped == True): tempDrawDir = 0
    if (board.turn) and (flipped == True): tempDrawDir = 0
    boardCanvas.create_rectangle(xpos + 3 * tempDrawDir, ypos + 3 * tempDrawDir, (xpos + squareSize + 3 * tempDrawDir),
                                 (ypos + squareSize + 3 * tempDrawDir), fill=col, outline=col)
    # redraw piece
    piece = str(board.piece_at(boardIndex))
    pieceFile = ''
    if (piece == 'R'): pieceFile = 'pieces\WR.png'  # white rook
    if (piece == 'N'): pieceFile = 'pieces\WN.png'  # white knight
    if (piece == 'B'): pieceFile = 'pieces\WB.png'  # white bishop
    if (piece == 'Q'): pieceFile = 'pieces\WQ.png'  # white queen
    if (piece == 'K'): pieceFile = 'pieces\WK.png'  # white king
    if (piece == 'P'): pieceFile = 'pieces\WP.png'  # white pawn

    if (piece == 'r'): pieceFile = 'pieces\BR.png'  # black rook
    if (piece == 'n'): pieceFile = 'pieces\BN.png'  # black knight
    if (piece == 'b'): pieceFile = 'pieces\BB.png'  # black bishop
    if (piece == 'q'): pieceFile = 'pieces\BQ.png'  # black queen
    if (piece == 'k'): pieceFile = 'pieces\BK.png'  # black king
    if (piece == 'p'): pieceFile = 'pieces\BP.png'  # black pawn
    if (pieceFile != ''):
        # app.img[count] = ImageTk.PhotoImage(file=pieceFile)
        # boardCanvas.create_image((xpos), (ypos), image=app.img[count], anchor=NW)

        img = Image.open(pieceFile)
        img = img.resize((squareSize - 0, squareSize - 0), Image.ANTIALIAS)
        app.img[boardIndex] = ImageTk.PhotoImage(img)
        boardCanvas.create_image(xpos + 3 * tempDrawDir, ypos + 3 * tempDrawDir, image=app.img[boardIndex], anchor=NW)
    count += 1
    pass


def main():
    global p1
    global p2
    global p1engine, p2engine
    global boardCanvas
    global canvasSize
    global app
    global root
    global board
    global clickDragging
    global flipped
    global gameStateVar, gameStateLabel
    global engine1
    global engine2
    global keeprunning
    global gameinprogerss

    gameinprogress = False

    flipped = False
    clickDragging = False

    root = tk.Tk()

    # position/dimensions for main tk frame
    x = 100
    y = 100
    w = 687
    h = 505
    oldappheight = h
    oldappwidth = w
    geostring = "%dx%d+%d+%d" % (w, h, x, y)

    root.geometry(geostring)
    app = TkFrame(root)
    app.bind("<Configure>", appresize)

    boardCanvas = Canvas(app, width=480, height=480)

    boardCanvas.bind("<Button-1>", canvasClick)
    boardCanvas.bind("<ButtonRelease-1>", canvasRelease)
    boardCanvas.bind("<B1-Motion>", canvasMotion)

    boardCanvas.pack(expand=YES)
    boardCanvas.place(x=0, y=0)

    gameStateVar = StringVar()

    gameStateLabel = Label(root, font=('calibri', 15), justify=LEFT, anchor="w", textvariable=gameStateVar)
    gameStateLabel.pack()
    gameStateLabel.place(x=0, y=480)

    p1 = "AI"
    p2 = "AI"

    if (p1 == "AI"):
        # engine1 = chess.engine.SimpleEngine.popen_uci("c:\\engines\\stockfish.exe")
        pass
    if (p2 == "AI"):
        # engine2 = chess.engine.SimpleEngine.popen_uci("c:\\c\\chess\\raven0.80.exe")
        pass

    initGame(p1, p2)
    # root.update()

    drawBoard()
    drawPieces()
    # root.after(1, mainloop())

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


def on_closing():
    global root
    global engine1
    global engine2
    if (p1 == "AI"): engine1.close()
    if (p2 == "AI"): engine2.close()
    root.destroy()


def initGame(player1, player2):
    global board
    global gameinprogress
    global gameStateVar

    board = chess.Board()
    gameinprogress = True
    gameStateVar.set("White to move.")
    if (p1 == "AI" and board.turn):
        getAIMove(turn='white')
    elif (p2 == "AI" and not board.turn):
        getAIMove(turn='black')


main()
# cProfile.run('foo()')
