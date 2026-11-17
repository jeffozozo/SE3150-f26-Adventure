from object import Object
from player import Player

class Brand(Object):
    def __init__(self):
        self.name = "brand"
        self.description = "description"
        self.can_be_gotten = "can_be_gotten"
        self.state = "state"
        self.visible = "visible"
        
    # this is the overloaded object.use command. If you make a new object, you have to implement this. 
    def use(self):
        pass


class Room:
    def __init__(self):
        self.room_num = 2
        self.description = "Room 2."
        self.riddle=""
        self.exits = ['up','east','south','north','west','down']
        self.objects = []
        self.order=['east','up','south','north','west','down']
        self.riddle_step=0

    def enter(self, player):
            player.current_room = self.room_num
            self.describe_room()
            while True:
                parts = input("> ").lower().split(maxsplit=1)
                if not parts:
                    continue
                command = parts[0]
                target = parts[1].strip() if len(parts) > 1 else ""
    
                if command in ["go", "move"]:
                    direction = self.move(target)
                    if direction is not None:
                        return direction
                elif command == "look":
                    if not target:
                        self.describe_room()
                    else:
                        #make targets to look at here
                        print("Nothing to describe.")
                elif command == "inventory":
                    player.show_inventory()
                elif command == "stats":
                    player.print_stats()
                elif command in ["help", "?"]:
                    print("Commands: go, move, look, inventory, stats, help, hint, quit")
                    print("Exits: " + ", ".join(self.exits))
                elif command == "hint":
                    print("Exits: " + ", ".join(self.exits))
                elif command == "quit":
                    if input("Are you sure? (y/n) ").lower().startswith("y"):
                        player.print_stats()
                        return "quit"
                else:
                    print("Command unavailable.")

    def describe_room(self):
        print(self.description)
        print("Exits: " + ", ".join(self.exits))
        
    def move(self, direction):
        direction = {"w": "west", "u": "up", "d": "down","e": "east","s": "south","n": "north"}.get(direction, direction)
        if direction in self.exits:
            return direction
        print("You can't go that way.")
        return None