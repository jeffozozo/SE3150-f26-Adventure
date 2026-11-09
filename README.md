# CS3150-Adventure

This is the repository for the template code to setup the Utah Tech CS-3150 crowd sourced adventure game. The intention of this project is that each student in class will build a ROOM that is part of a whole adventure game. The rooms are linked together by a MAP (really a bi-directional connected graph of rooms) that the PLAYER will traverse during their adventure. 

The students will need to follow some precise specifications in order for their rooms to work. This is what needs to happen:


1. The instructor will issue a map file that contains a list of rooms and the students they belong to. 
2. The room in the map document will list what exits need to be implemented.
3. The map.txt will start at room 1 for student assignments and will specify what 'exits' the student's rooms need to support.
5. The instructor will produce Room0_instructorName.py as the introductory room. When the player exits room 0 they will be in room 1.
9. The current map.txt is shown here for reference. It contains four rooms, all authored by jeff:

```text
Room:0:jeff
 down,1

Room:1:jeff
 east,2
 north,3

Room:2:jeff
 west,1
 up,3

Room:3:jeff
 down,2
```

 11. The students will need to create the rooms associated with their name. They will look at the connections to their room and make sure that their descriptions match those connections and that the player can GO or MOVE in those directions. Here are the requirements for the rooms:
 12. Rooms are written as **stand alone python programs.** The file name is important and must follow the specification: Room[number]_[student_name].py
 14. EVERY ROOM  must support the following commands at a minimum:
     
+ **go, move [direction]** - allows the player to move to the next Room. Players can only move in the directions allowed by the specification for the room. 
+ **look [item]** - provides a description of the item. the item can be in the player's inventory or it can be in an object array in the room. If no [item] is given, the room description is printed.
+ **get, take [item]** - allows the player to pick up the item and put it into their inventory. The room must create an object of type Object for the player to pick it up. (See Objects) below.
+ **drop [item]** - allows the player to remove an item from their inventory and place it in the room's list of Objects.
+ **inventory** - prints out the items in the PLAYERs inventory.
+ **stats** - prints out the PLAYERs statistics
+ **help,?** - prints out the list of commands
+ **hint** - prints out a room-specific hint that will help the player get through the puzzle in the room
+ **quit** - asks "Are you sure? (y/n) and if y prints out the player stats and ends the game.

15. Rooms can also support any custom commands that will support solving the puzzle. For example, a room could have a fountain in it, and the PLAYER could say "drink fountain" and the room would respond with a result. If the puzzle is hard, giving a hint is a good idea to keep the players from rage quitting.
16. **OBJECTS** - PLAYERS have an inventory and rooms have a list of Objects. Rooms must support dropping items so they MUST support an object list in some way. It doesn't matter what the room's object list is called, only that when a player drops something it goes out of the inventory and into the room's object list. If the player wants to get the object again, they should be able to do so, unless it is part of the puzzle of the room. You could also make it so that the object would get destroyed if they did something crazy with it. Like there could be a pit in the room and the PLAYER could say "throw lamp in pit" and the result could be that the lamp is now gone.
    + All game Objects must inherit from a base Object class that has a **pure virtual** function called "use"
    + You create an object by subclassing Object and implementing the use function.
    + The lamp in Room0 is the example of how to implement an object. Take a look at the lamp defined in Room0.
17. The students should try to write the room descriptions so that they indicate the exits available in the room so that the game is playable. However, if you want to implement a secret exit, pick one of your exits and make sure it isn't obvious. Require the player to 'search' or something and then reveal the exit by changing the description of the room on the fly. You have a TON of flexibility of what you can do in your room.
18.  When the room is complete the **room should return the direction that the PLAYER has chosen or that is the result of the solution to the puzzle.** For example if the PLAYER chooses "north" and that is a valid direction, the program should end and return "north". The room MUST ONLY return directions that were part of it's assignment in the map.txt file. 

This repo has the following files:
+ map.txt - the map file
+ player.py - the class representing the player
+ Room0_jeff.py	- an example starter room
+ Room1_example.py - placeholder room
+ Room2_example.py - placeholder room
+ Room3_example.py - placeholder room
+ Adventure.py - the game 'engine' 
+ object.py - the base class for objects	
+ README.md - this file

Adventure.py is the engine - it runs the rooms and orchestrates the action. You should not make changes to Adventure.py - this will be the way the class runs the whole game. It is here for your reference. If you find bugs in it or wish to make material changes, discuss these with the instructor.

Once all of the rooms have been created, when they are placed in the same directory as Adventure.py, you just run Adventure.py and the rooms will load and you can play. The rooms have to correctly return the exits they are supposed to return as describe in map.txt or the game will crash. Here are some other considerations:

+ Look at the definition of Objects in object.py. You can use the attributes of the object to do things like make objects that are too big to get or that are attached to something. You can have puzzles that change those settings and then they can allow changes in the way that the players interact with the objects.
+ Objects will travel with the player from room to room in the player's inventory. You should coordinate with other Room Authors to get an object in some room, and then use it in another.
+ rooms can change player stats. Rooms that do cool things should give the player a boost to their score. If players do dumb things you can hurt them by removing health. You might be generous and make an Object that the player could use to restore their health. You can also change the Player's condition - they could be any condition that you want. This can also pass from room to room and could affect the way play happens. For example, in one room, a person could fall in a river and be wet and cold. If they go to another room that is a wintery scene, say by an Ice Dragon, the person could freeze to death if they are cold and wet. The game would be over for them, and next time they wouldn't fall in the river. This is a very important dynamic and should be utilized!
+ Objects also have a state. On, off, broken, glowing, whatever. Use that to create interesting things across rooms as well. Note that the lamp is on or off. Note that in the example room1 that the room is pitch dark if the lamp is off. This is a cool dynamic that can be used as well.

Lastly, the primary purpose for this activity is for you to have some fun. Do something cool - spend some good time on it, think about it and make it worthwhile. The whole game will be better for your efforts. 

Also remember that we will be reviewing each other's code. If your code is entirely generated by AI, and someone is reviewing it, and asks you questions, it is not acceptable to say "I don't know." You must take responsibility for your code. Write as much of it as you can. Get the AI to help you if you like, but take full ownership of the code it produces. 
