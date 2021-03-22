# Bogert
Playing around with some chess AI!

"Let that clockwork contraption solve the entire problem for you!"

# TODO:

- Improve the evaluation function:
    - King mid vs endgame table
    - Pawn Structure (https://www.chessprogramming.org/Pawn_Structure)
    - Queen wandering (https://www.chessprogramming.org/Evaluation_of_Pieces#cite_note-1) - this would be a good start!

- Improve the search logic:
    - Order the possible moves such that takes are searched first, should increase the amount of pruning
        - Done with iterative deepening, can expand to PVS/Aspiration window
    - Transposition to remove prev branches https://www.chessprogramming.org/Transposition
    - Quiescence search for increased stability of end nodes https://en.m.wikipedia.org/wiki/Quiescence_search - this is a major problem at the moment due to shallow depth/horizon 

- Lookups:
    - Add some form of end game table - currently it has no mate sense
    - Add in an opening play book, can get stuck running knights around the board at the start!

- Meta data:
    - Export games as PGNs so they can be evaluated on lichess.com
    - Get better evaluation metrics for search nodes etc

- Fun stuff:
    - Get it running on Lichess as a bot! (https://github.com/ShailChoksi/lichess-bot)
    
- Admin:
    - Tidy up the code
