from object import Object
from player import Player
from Room0_jeff import Lamp


class FragileHammer(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the superclass constructor
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # the lamp toggles when you 'use' it. 
        if self.state == "working":
            self.state = "broken"
            print(f"The hammer breaks upon use.")
        else:
            print(f"The hammer is broken and unusable.")

class Room:
    def __init__(self):
        self.room_num = 1
        self.description = "Stone bricks line the walls and floors in varrying states of decay. Along the walls are the remains of shelfs and racks." \
                           "Tables are strewn about the room destroyed and rotten, there might be something usefull in the mess. In the center lays a " \
                           "ladder going down into a hole with dilapitated railings, and next to it is one non destroyed table with a sturdy vase on top. " \
                           "aroud it. In the center of the north and east walls are holes carved out of the stone and tunnels running into the dark. " \
                           "Before each of the exits to this room are markings of some sort, each unique to the exit."
        self.exits = ['north', 'east', 'down'] # North to 13, East to 14, Down to 2.
        self.objects = []

    def enter(self, player):
        # Give the descrition of room as they enter from floor 0
        if(player.current_room == 0):
            print("As you open your eyes and find youself somewhere entirely new. A wave a nausea crashes into you momentarily as you " \
                  "look around. Shadows dance along the floor as torches flicker behind you.")
        #Set the players room to current room
        player.current_room = self.room_num

        #Check to see if player has lantern before getting the lantern state
        lampState = "off"
        if player.has_item("lamp"):
            lampState = player.get_item("lamp").state

        #Describe the Room depending on the lantern state, either on or off.
        self.describe_room(lampState)

        #Begin listening for the players input
        while True:
            parts = input("> ").lower().split(maxsplit=1)
            if not parts:
                continue
            command = parts[0]
            target = parts[1].strip() if len(parts) > 1 else ""

            if command in ["go", "move"]:
                self.move(target)
            elif command == "look":
                self.look(target, player)
            elif command == "search":
                self.search(player)
            elif command == "drop":
                self.drop(target, player)
            elif command == "use":
                self.use(target, player)
            elif command == "inventory":
                self.show_inventory(player)
            elif command == "stats":
                self.show_stats(player)
            elif command in ["help", "?"]:
                self.show_help()
            elif command == "hint":
                self.show_hint()
            elif command == "quit":
                self.quit_game(player)
            else:
                self.unknown_command

    def describe_room(self, lampState):
        if(lampState == "on"):
            print(self.description)
            if self.objects:
                for obj in self.objects:
                    print(f"There is a {obj.name} here.")
        else:
            print("Beyond the light of the torches behind you the room is bathed in darkness.")
        

    def move(self, direction):
        if direction in ["n","N","North","north","e","E","East","east","d","D","Down","down","hole","Hole","ladder","Ladder"]:
            print("You travel " + direction) #Lazy way, no unique descriptions on travel

            travelDirection = ""
            if(direction in ["n","N","North","north"]): travelDirection = "north"
            if(direction in ["e","E","East","east"]): travelDirection = "east"
            if(direction in ["d","D","Down","down","hole","Hole","ladder","Ladder"]): travelDirection = "down"

            return travelDirection
        else:
            print("You can't go that way.")
            return None

    def drop(self, item_name, player):
            item = self.get_item_from_inventory(item_name,player)
            if(item == None):
                print(f"You don't have the {item_name}.")
                return
            
            # remove the item from the inventory and put it in the object list
            player.inventory.remove(item)
            self.objects.append(item)
            print(f"You drop the {item.name}.")
            return 

    def use(self, item_name, player):
            item = self.get_item_from_inventory(item_name,player)
            
            #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
            if(item == None):
                print("you can't use that.")
                return
            if(item == "fragilehammer"):
                print("You smash open the vase, and the dusty remains of something long lost to time scatters into the air. Nothing else is found.")
            item.use()

    def look(self, target, player):
            if(target == None or target == "" ):
                self.describe_room()
                return

            #Check which wall they are looking at and describe the warning
            if target == "n" or "N" or "north" or "North":
                print("Near the north exit are drawings made by someone before you, skulls in a pile with a pair of eyes staring at you sitting above them.")
            if target == "e" or "E" or "east" or "East":
                print("A dark pit is scrawled against the stone with an closed eye next to it.")
            if target == "d" or "D" or "Down" or "down" or "hole" or "Hole":
                print("A door is drawn on the floor with chains and lock on it.")
            
            # Check if the object is in the room or in the player's inventory and print it description and status. You can use this code exactly.
            item = self.get_item_from_inventory(target,player)
            if item == None:
                item = self.get_item_from_object_list(target)
                if item == None:
                    print("There is nothing like " + target + " to look at.")
                    return
    
            if target == item.name.lower().strip():
                print(item.description) 
                if(item.state != None): 
                    print(f"The {item.name} is {item.state}")                   
                return

    def search(self, player):
        print("Amoung the crashed shelves you find an old, fragile hammer.")
        fragilehammer = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "working", True)
        player.inventory.append(fragilehammer)

    def show_inventory(self, player):
            player.show_inventory()
    
    def show_stats(self, player):
        player.print_stats()

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith('y'):
            player.print_stats()
            return "quit"

    def show_help(self):
        print("Commands: go, move, look, search, drop, use, inventory, stats, help, hint, quit")
    
    def show_hint(self):
        print("There might be something useful in the vase if you can find something to break it.")

    def unknown_command(self):
        print("You can't do that here. Try something else or type 'help' for options or 'hint' for a clue.")