#include "game.h"
#include <time.h>


int main() {
    srand(time(0));

    Game game;
    
    while (game.readNextTurnData())
        game.respondToTurn();

    return 0;
}
