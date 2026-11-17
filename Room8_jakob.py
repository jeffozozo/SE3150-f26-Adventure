from object import Object


class Bonfire(Object):
    def use(self):
        self.state = "lit"
        self.description = "A steady bonfire burns brightly among the ashes."


class Room:
    def __init__(self):
        self.room_num = 8
        self.description = (
            "You enter the Forgotten Shrine, a quiet stone chamber hidden beneath "
            "the ruins of a kingdom.\n"
            "A dying bonfire glows among the ashes, its warmth barely reaching "
            "the cold walls.\n"
            "A passage leads east, while a worn stairway climbs up into darkness."
        )
        self.exits = ['east', 'up']
        self.objects = [
            Bonfire(
                "Dying Bonfire",
                "A small flame struggles to burn among the ashes.",
                False,
                "dying",
                True,
            ),
            Object(
                "Weathered Tombstone",
                "Its inscription reads: 'A hidden ember may wake the flame.'",
                False,
                None,
                True,
            ),
            Object(
                "Broken Knight's Sword",
                "A faded symbol is engraved near the broken blade.",
                False,
                "broken",
                True,
            ),
            Object(
                "Rusty Armor",
                "The armor belonged to a knight who once guarded the shrine.",
                False,
                "rusted",
                True,
            ),
            Object(
                "Ancient Ashes",
                "A pile of cold ashes lies beside the bonfire.",
                False,
                None,
                True,
            ),
            Object(
                "Ancient Ember",
                "A small ember hidden among the ashes.",
                True,
                "glowing",
                False,
            ),
        ]

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
                    print(self.look(target))
            elif command in ["get", "take"]:
                print(self.get(target, player))
            elif command in ["drop", "put"]:
                print(self.drop(target, player))
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
        for obj in self.objects:
            if obj.visible:
                print(f"There is a {obj.name} here.")
        print("Exits: " + ", ".join(self.exits))

    def look(self, target):
        if target.lower() == "ancient ashes":
            for obj in self.objects:
                if obj.name == "Ancient Ember":
                    obj.visible = True
                    return "You find a hidden ember in the ashes."

        for obj in self.objects:
            if obj.name.lower() == target.lower():
                return obj.description
        return "There is nothing like " + target + " to look at."

    def get(self, item_name, player):
        for obj in self.objects:
            if obj.name.lower() == item_name.lower():
                if not obj.visible:
                    return item_name + " is not here."
                if not obj.can_be_gotten:
                    return "The " + obj.name + " cannot be taken."
                player.inventory.append(obj)
                self.objects.remove(obj)
                return "You take the " + obj.name + "."
        return item_name + " is not here."

    def drop(self, item_name, player):
        for obj in player.inventory:
            if obj.name.lower() == item_name.lower():
                player.inventory.remove(obj)
                self.objects.append(obj)
                return "You drop the " + obj.name + "."
        return "You don't have the " + item_name + "."

    def move(self, direction):
        direction = {"e": "east", "u": "up"}.get(direction, direction)
        if direction in self.exits:
            return direction
        print("You can't go that way.")
        return None
