from object import Object
from player import Player

class Room:
    def __init__(self):
        self.room_num = 10
        self.description = (
            "A dusty library. Bookshelves line the walls, and a heavy "
            "wooden chest sits in the center."
        )
        self.exits = ["east", "up", "down"]

        self.key = Object("key", "A small brass key.", "tarnished", True, True)
        self.chest = Object(
            "chest",
            "A heavy wooden chest with a brass lock.",
            "locked",
            False,
            True
        )
        self.objects = [self.key, self.chest]

    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room()

        while True:
            command = input("> ").lower().strip()
            parts = command.split(" ", 1)
            command_base = parts[0]
            other_part = parts[1] if len(parts) > 1 else ""

            if command_base in ["move", "go"]:
                next_room = self.move(other_part)
                if next_room is not None:
                    return next_room
            elif command_base in ["get", "take"]:
                self.get(other_part, player)
            elif command_base == "use":
                self.use(other_part, player)
            elif command_base == "look":
                self.look(other_part, player)
            elif command_base == "inventory":
                player.show_inventory()
            elif command_base == "quit":
                if self.quit_game(player) == "quit":
                    return "quit"
            elif command_base in ["help", "?"]:
                self.show_help()
            else:
                print("You can't do that here.")

    def describe_room(self):
        print(self.description)
        for obj in self.objects:
            print(f"There is a {obj.name} here.")

    def move(self, direction):
        directions = {
            "east": "east",
            "e": "east",
            "up": "up",
            "u": "up",
            "down": "down",
            "d": "down"
        }

        if direction in directions:
            direction = directions[direction]
            print(f"You head {direction}.")
            return direction

        print("You can't go that way.")
        return None

    def get(self, item_name, player):
        item = self.get_item_from_object_list(item_name)

        if item is None:
            print(f"{item_name} is not here.")
            return

        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        player.inventory.append(item)
        self.objects.remove(item)
        print(f"You take the {item.name}.")

    def use(self, item_name, player):
        if item_name == "key":
            if player.has_item("key"):
                if self.chest.state in [True, "unlocked"]:
                    print("The chest is already unlocked.")
                else:
                    self.chest.state = "unlocked"
                    self.chest.description = (
                        "A heavy wooden chest, now unlocked. "
                        "It contains a pile of gold!"
                    )
                    print("You use the key to unlock the chest. It clicks open.")
            else:
                print("You don't have the key.")
        else:
            print("You can't use that here.")

    def look(self, target, player):
        if target == "":
            self.describe_room()
            return

        item = self.get_item_from_inventory(target, player)

        if item is None:
            item = self.get_item_from_object_list(target)

        if item is not None:
            print(item.description)
            print(f"The {item.name} is {item.state}.")
        else:
            print(f"There is nothing like {target} to look at.")

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith("y"):
            return "quit"

    def show_help(self):
        print(
            "Available commands: move, go, look, get, take, "
            "use, inventory, quit, help"
        )

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


#testing again testing again for the third time
