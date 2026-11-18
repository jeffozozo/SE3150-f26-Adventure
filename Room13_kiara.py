class Room:
    def __init__(self):
        self.room_num = 13
        self.description = (
            "Room 13 is a dark, cool cave. A dragon sleeps nearby, its "
            "heavy breathing echoing off the walls."
        )
        self.exits = ["south", "east", "west", "down"]
        self.actions_before_dragon_wakes = 3
        self.actions_taken = 0
        self.cave_is_lit = False

    def enter(self, player):
        player.current_room = self.room_num

        if not player.has_item("lamp"):
            print("You have no lamp to see or escape. The dragon wakes and eats you!")
            player.health = 0
            player.print_stats()
            return "quit"

        self.describe_room()
        print(
            "You have only three actions before the dragon wakes. "
            "Use your lamp, then leave through an exit. You have a few options: south, east, west, down"
        )

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
                if target in ["", "cave", "room"]:
                    self.describe_room()
                elif target == "dragon":
                    print("The dragon is asleep, but it will not stay that way for long. Use the lighter to find the exits")
                elif target == "lighter": 
                    print("Your lighter can illuminate the cave. Use it now.")
                else:
                    print("You can't see anything else in the darkness.")
            elif command == "use":
                if target == "lamp" and player.has_item("lamp"):
                    self.cave_is_lit = True
                    print("You light your lamp. The cave's exits are visible!")
                    print("Exits: " + ", ".join(self.exits))
                else:
                    print("You can only use the lamp you brought with you.")
            elif command == "inventory":
                player.show_inventory()
            elif command == "stats":
                player.print_stats()
            elif command in ["help", "?"]:
                print("Commands: go <direction>, move <direction>, use lamp, look, inventory, stats, hint, quit")
                print("Exits: " + ", ".join(self.exits))
            elif command == "hint":
                print("Use your lamp, then go south, east, west, or down before the dragon wakes.")
            elif command == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
                continue
            else:
                print("Command unavailable. Type 'help' or 'hint' for guidance.")

            self.actions_taken += 1
            actions_left = self.actions_before_dragon_wakes - self.actions_taken
            if actions_left > 0:
                print(f"The dragon stirs. {actions_left} action(s) left!")
            else:
                print("The dragon wakes, catches you in the cave, and eats you!")
                player.health = 0
                player.print_stats()
                return "quit"

    def describe_room(self):
        print(self.description)
        if self.cave_is_lit:
            print("Your lamp reveals the cave exits: " + ", ".join(self.exits))
        else:
            print("It is too dark to see the exits. You hear a dragon sleeping nearby.")

    def move(self, direction):
        direction = {
            "s": "south",
            "e": "east",
            "w": "west",
            "d": "down",
        }.get(direction, direction)
        if direction in self.exits:
            print(f"You hurry {direction}, escaping the cave before the dragon wakes.")
            return direction

        print("You can't go that way.")
        return None
