from object import Object


class CaveItem(Object):
    def use(self):
        pass


class Room:
    def __init__(self):
        self.room_num = 13
        self.description = (
            "The Dragon's Cave is dark and cold. Skulls and bones lie around a large sleeping dragon."
        )
        self.exits = ["south", "east", "west", "down"]
        self.objects = [
            CaveItem(
                "Key",
                "A small iron key. It may unlock the eastern door.",
                True,
                None,
                True,
            ),
            CaveItem(
                "Hammer",
                "A sturdy hammer. It may break through the western stone barrier.",
                True,
                None,
                True,
            ),
        ]
        self.actions_before_dragon_wakes = 4
        self.actions_taken = 0
        self.cave_is_lit = False
        self.trapdoor_found = False
        self.player = None

    def enter(self, player):
        player.current_room = self.room_num
        self.player = player
        self.actions_taken = 0
        self.cave_is_lit = False
        self.trapdoor_found = False

        if not player.has_item("lamp"):
            print("You have no lamp. The dragon attacks and kills you!")
            player.health = 0
            player.print_stats()
            return "south"

        self.describe_room()
        print(
            "The dragon is asleep. You have four actions before it wakes. "
            "Help, hint, inventory, stats, and blocked exits do not use an action."
        )

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]
            other_part = parts[1].strip() if len(parts) > 1 else ""
            used_action = False

            if command_base in ["go", "move"]:
                direction = self.move(other_part, player)
                if direction is not None:
                    return direction
                used_action = other_part in ["down", "d"] and self.trapdoor_found
            elif command_base == "use":
                used_action = self.use(other_part, player)
            elif command_base == "look":
                self.look(other_part, player)
                used_action = True
            elif command_base in ["get", "take"]:
                used_action = self.get(other_part, player)
            elif command_base in ["drop", "put"]:
                used_action = self.drop(other_part, player)
            elif command_base == "inventory":
                player.show_inventory()
            elif command_base == "stats":
                player.print_stats()
            elif command_base in ["help", "?"]:
                self.show_help()
            elif command_base == "hint":
                self.show_hint()
            elif command_base == "search":
                used_action = self.search()
            elif command_base == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
            else:
                self.unknown_command()

            if used_action:
                self.actions_taken += 1
                actions_left = self.actions_before_dragon_wakes - self.actions_taken
                if actions_left > 0:
                    print("The dragon stirs. " + str(actions_left) + " action(s) left!")
                else:
                    print("The dragon wakes and eats you!")
                    player.health = 0
                    player.print_stats()
                    return "south"

    def describe_room(self):
        print(self.description)
        if not self.cave_is_lit:
            print("It is too dark to see the exits or anything else in the cave.")
            return

        visible_exits = [exit_name for exit_name in self.exits if exit_name != "down"]
        if self.trapdoor_found:
            visible_exits.append("down")
        print("Your lamp reveals the exits: " + ", ".join(visible_exits))

        for item in self.objects:
            print("There is a " + item.name.lower() + " here. " + item.description)

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

        if direction in ["east", "west", "down"] and not self.cave_is_lit:
            print("It is too dark to see that way. Use your lamp first.")
            return None

        if direction == "east":
            if player is not None and player.has_item("key"):
                print("You unlock the eastern door and enter Room 7.")
                return "east"
            print("The eastern door is locked. You need the key.")
            return None

        if direction == "west":
            if player is not None and player.has_item("hammer"):
                print("You break the cracked stone barrier and enter Room 3.")
                return "west"
            print("The western passage is blocked. You need the hammer.")
            return None

        if direction == "down":
            if not self.trapdoor_found:
                print("You cannot see a way down. Search the cave for a hidden exit.")
                return None
            print("A trapdoor asks: I have no lungs, but I need air.")
            print("I have no mouth, but water kills me. What am I?")
            answer = input("Answer: ").lower().strip()
            if answer == "fire":
                print("The trapdoor opens and you enter Room 17.")
                return "down"
            print("The trapdoor remains closed.")
            return None

        print("You can't go that way.")
        return None

    def use(self, item_name, player):
        if item_name.lower() == "lamp" and player.has_item("lamp"):
            if self.cave_is_lit:
                print("The lamp is already lighting the cave.")
                return False
            lamp = self.get_item_from_inventory("lamp", player)
            if lamp is not None:
                lamp.state = "on"
            self.cave_is_lit = True
            print("You light the lamp. The cave exits and its objects are now visible.")
            self.describe_room()
            print("Take either the key for the eastern door or the hammer for the western passage.")
            return True

        print("You can't use that.")
        return False

    def look(self, target, player):
        if target in ["", "cave", "room"]:
            self.describe_room()
        elif target == "dragon":
            print("The dragon is asleep, but it is beginning to stir.")
        elif target == "lamp":
            print("The lamp can illuminate the dark cave.")
        else:
            item = self.get_item_from_inventory(target, player)
            if item is None and self.cave_is_lit:
                item = self.get_item_from_object_list(target)
            if item is not None:
                print(item.description)
            elif not self.cave_is_lit and self.get_item_from_object_list(target) is not None:
                print("It is too dark to see that.")
            else:
                print("There is nothing like that to look at.")

    def get(self, item_name, player):
        if item_name == "":
            print("Get what?")
            return False
        item = self.get_item_from_object_list(item_name)
        if item is None:
            print(item_name + " is not here.")
            return False
        if not self.cave_is_lit:
            print("It is too dark to see or take anything.")
            return False
        if player.has_item(item_name):
            print("You already have the " + item.name.lower() + ".")
            return False
        if item.name.lower() in ["key", "hammer"] and (
            player.has_item("key") or player.has_item("hammer")
        ):
            print("You can carry only one route item. Drop your current choice first.")
            return False
        if not item.can_be_gotten:
            print("The " + item.name + " cannot be taken.")
            return False
        player.inventory.append(item)
        self.objects.remove(item)
        print("You take the " + item.name.lower() + ".")
        return True

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item is None:
            print("You don't have " + item_name + ".")
            return False
        player.inventory.remove(item)
        self.objects.append(item)
        print("You drop the " + item.name.lower() + ".")
        return True

    def search(self):
        if not self.cave_is_lit:
            print("It is too dark to search. Use your lamp first.")
            return False
        if self.trapdoor_found:
            print("You have already found the trapdoor.")
            return False
        self.trapdoor_found = True
        print("You find a concealed trapdoor beneath a pile of bones.")
        self.describe_room()
        return True

    def show_help(self):
        print("Commands: go, move, look, use, get, take, drop, search")
        print("inventory, stats, help, hint, quit")

    def show_hint(self):
        print("Use the lamp to reveal the cave. Take the key for east or hammer for west.")
        print("Search the cave to find the hidden trapdoor. Its riddle answer is fire.")

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
