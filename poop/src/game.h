#ifndef GAME_H
#define GAME_H

#include <cstdlib>
#include <iostream>
#include <string>
#include "nlohmann/json.hpp"
#include "types.h"


using json = nlohmann::json;
using namespace std;

class Game {
public:
    string tankId;  // Your client's tank id
    json currentTurnMessage;  // The last received message (updated in readNextTurnData)
    map<string, json> objects;  // All the objects with the same format as described in the doc. The key will be object id and value will be the object itself.
    double width;  // The width of the map.
    double height;  // The height of the map.

    json readAndParseJSON() {
        /*
            Reads one line of input from stdin and parses it as JSON.
            It will return the parsed JSON or if parsing failed, it will return the string "Failed".
        */
        
        // Read input from stdin
        string input;
        getline(cin, input);
        
        // Parse input as JSON
        try {
            json parsedInput = json::parse(input);
            return parsedInput;   
        } catch (json::parse_error& e) {
            cerr << "Error parsing JSON: " << e.what() << endl;
            return "Failed";
        }
    }

    Game() {
        /*
            The default constructor for the Game object.
            It will take care of the world init messages here and will save all map objects in the "objects" attribute.
            By the time the constructor is done and the object is created, the game has sent all init messages and the main
            communication cycle is about to begin.
        */

        // Read the first line to see our tank's id
        json firstMessage = readAndParseJSON();
        tankId = firstMessage["message"]["your-tank-id"];

        // Now start reading the map info until the END_INIT signal is received.
        json nextMessage = readAndParseJSON();
        while (nextMessage != "END_INIT") {
            // Get the updated_objects part
            json updatedObjects = nextMessage["message"]["updated_objects"];

            // Loop through all passed objects and save them
            for (json::iterator it = updatedObjects.begin(); it != updatedObjects.end(); ++it) {
                objects[it.key()] = it.value();
            }

            // Read the next message
            nextMessage = readAndParseJSON();
        }

        // We are outside the loop now, which means END_INIT signal was received.

        // Let's figure out the size of the map based on the given boundaries.
        // Set width and height = 0 then find the maximum x and y - they have to be the width and height of the map.
        width = 0;
        height = 0;
        for (auto object_it: objects) {
            if (object_it.second["type"] == BOUNDARY) {
                json position = object_it.second["position"];
                for (int i = 0; i < 4; i++) {
                    width = max(width, (double)position[i][0]);
                    height = max(height, (double)position[i][1]);
                }
            }
        }
    }

    bool readNextTurnData() {
        /*
            This function reads the data for this turn and returns true if the game continues (i.e. END signal is not received) otherwise
            it will return false.
        */
        currentTurnMessage = readAndParseJSON();

        // Return if the game is over
        if (currentTurnMessage == "END") return false;

        // First delete the objects that have been deleted.
        json deletedObjects = currentTurnMessage["message"]["deleted_objects"];
        for (auto deleted_id: deletedObjects) {
            // Delete the object from the map.
            // NOTE: You may want to do additional logic here e.g. check if a powerup you were moving towards is deleted, etc.
            objects.erase(deleted_id);
        }

        // Now add all the new/updated objects
        json updatedObjects = currentTurnMessage["message"]["updated_objects"];
        // Loop through all passed objects and save them
        for (json::iterator it = updatedObjects.begin(); it != updatedObjects.end(); ++it) {
            objects[it.key()] = it.value();
        }

        // Game continues!
        return true;
    }

    void respondToTurn() {
        /*
            Your logic goes here. Respond to the turn with an action. You can always assume readNextTurnData is called before this.
        */

        // Write your code here...

        // For demonstration, let's always shoot at a random angle for now.
        json response;
        response["shoot"] = rand() % 360;
        cout << response.dump() << endl;
    }

};

#endif  // GAME_H
