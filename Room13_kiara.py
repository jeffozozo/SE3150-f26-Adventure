class Room:
    def __init__(self):
        self.room_num = 13
        self.description = (
            "The Dragon's Cave is dark and cold. Skulls and bones lie around a large sleeping dragon."
        )
        self.exits = ["south", "east", "west", "down"]
        self.objects = []
        self.actions_before_dragon_wakes = 4
        self.actions_taken = 0
        self.cave_is_lit = False
        self.player = None

    def enter(self, player):
        player.current_room = self.room_num
        self.player = player
        self.actions_taken = 0

        if not player.has_item("lamp"):
            print("You have no lamp. The dragon attacks and kills you!")
            player.health = 0
            player.print_stats()
            return "quit"

        self.cave_is_lit = True
        self.describe_room()
        print("The dragon is asleep. Warning: it can wake before you escape.")

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]
            other_part = parts[1].strip() if len(parts) > 1 else ""

            if command_base in ["go", "move"]:
                direction = self.move(other_part, player)
                if direction is not None:
                    return direction
            elif command_base == "use":
                self.use(other_part, player)
            elif command_base == "look":
                self.look(other_part, player)
            elif command_base in ["get", "take"]:
                self.get(other_part, player)
            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)
            elif command_base == "inventory":
                player.show_inventory()
            elif command_base == "stats":
                player.print_stats()
            elif command_base in ["help", "?"]:
                self.show_help()
            elif command_base == "hint":
                self.show_hint()
            elif command_base == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
            else:
                self.unknown_command()

            self.actions_taken += 1
            actions_left = self.actions_before_dragon_wakes - self.actions_taken
            if actions_left > 0:
                print("The dragon stirs. " + str(actions_left) + " action(s) left!")
            else:
                print("The dragon wakes and eats you!")
                player.health = 0
                player.print_stats()
                return "quit"

    def describe_room(self):
        print(self.description)
        if self.cave_is_lit:
            print("Your lamp reveals the exits: " + ", ".join(self.exits))
        else:
            print("It is too dark to see the exits.")

    def move(self, direction, player=None):
        if player is None:
            player = self.player

        direction = {
            "s": "south",
            "e": "east",
            "w": "west",
            "d": "down",
        }.get(direction, direction)

        if direction == "south":
            print("You take the narrow passage back to Room 1.")
            return "south"

        if direction == "east":
            if player is not None and player.has_item("key"):
                print("You unlock the eastern door and enter Room 7.")
                return "east"
            print("The eastern door is locked. You need a key.")
            return None

        if direction == "west":
            if player is not None and player.has_item("hammer"):
                print("You break the cracked stone barrier and enter Room 3.")
                return "west"
            print("The western passage is blocked. You need a hammer.")
            return None

        if direction == "down":
            print("A trapdoor asks: I have no lungs, but I need air.")
            print("I have no mouth, but water kills me. What am I?")
            answer = input("Answer: ").lower().strip()
            if answer in ["fire", "fire.","Fire"]:
                print("The trapdoor opens and you enter Room 17.")
                return "down"
            print("The trapdoor remains closed.")
            return None

        print("You can't go that way.")
        return None

    def use(self, item_name, player):
        if item_name == "lamp" and player.has_item("lamp"):
            self.cave_is_lit = True
            print("You light the lamp. The cave exits are visible!")
        else:
            print("You can't use that.")

    def look(self, target, player):
        if target in ["", "cave", "room"]:
            self.describe_room()
        elif target == "dragon":
            print("The dragon is asleep, but it is beginning to stir.")
        elif target == "lamp":
            print("The lamp can illuminate the dark cave.")
        else:
            item = self.get_item_from_object_list(target)
            if item is None:
                item = self.get_item_from_inventory(target, player)
            if item is not None:
                print(item.description)
            else:
                print("There is nothing like that to look at.")

    def get(self, item_name, player):
        if item_name == "":
            print("Get what?")
            return
        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(item_name + " is not here.")
            return
        if not item.can_be_gotten:
            print("The " + item.name + " cannot be taken.")
            return
        player.inventory.append(item)
        self.objects.remove(item)
        print("You take the " + item.name + ".")

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print("You don't have " + item_name + ".")
            return
        player.inventory.remove(item)
        self.objects.append(item)
        print("You drop the " + item.name + ".")

    def show_help(self):
        print("Commands: go, move, look, use, get, take, drop")
        print("inventory, stats, hint, quit")

    def show_hint(self):
        print("Use the lamp. Keep a key and hammer in your inventory.")
        print("The trapdoor riddle answer is something that burns.")

    def unknown_command(self):
        print("Command unavailable. Type help for a list of commands.")

    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def get_item_from_object_list(self, item_name):
        for item in self.objects:
            if item.name.lower() == item_name.lower():
                return item
        return None
