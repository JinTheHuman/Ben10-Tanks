# CodeQuest 23 C++ Submission Template

Use this repo as starting point for your C++ submissions to CodeQuest 23.

## Running the code

To compile and test on your local, either compile with gcc:

```
g++ src/main.cpp -o game.out -std=c++11
```

and run:

```
./game.out
```

Or run using the docker image (which would ensure you get the same output as on CodeQuest servers) from the root directory:

```
docker build . -t my-submission:latest
docker run -it my-submission:latest
```

## Working on your bot

All functions in the code are commented so I would recommend checking the comments first.

Most logic of the game is inside the `Game` class. The input is already read and parsed for you. You can, if you need, change the
input reading logic.

The main part of the code you should change is `Game::respondToTurn`. Use the `objects` attribute to process what's happening in the game and respond with an action.