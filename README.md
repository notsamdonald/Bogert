# Bogert
Playing around with some chess AI!

"Let that clockwork contraption solve the entire problem for you!"

# TODO:


- Improve the evaluation function:
    - King mid vs endgame table
    - Pawn Structure (https://www.chessprogramming.org/Pawn_Structure)
    - Queen wandering (https://www.chessprogramming.org/Evaluation_of_Pieces#cite_note-1) - this would be a good start!
- Improve the search logic:
    - Transposition to remove prev branches https://www.chessprogramming.org/Transposition
- Add some form of end game table - currently it has no mate sense
- Add in an opening play book, can get stuck running knights around the board at the start!
- Export games as PGNs so they can be evaluated on lichess.com

- Order the possible moves such that takes are searched first, should increase the amount of pruning
    - Done with iterative deepeing, can expand to PVS/Aspiration window
    - Add in some metics for evaluating these changes
