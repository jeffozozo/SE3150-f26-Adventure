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
            "A passage leads east and a worn stairway climbs up, but both are "
            "sealed by the dying flame."
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
                "Its inscription reads: 'Where the knight's flame symbol rests, "
                "a hidden ember waits to wake the fire.'",
                False,
                None,
                True,
            ),
            Object(
                "Broken Knight's Sword",
                "A faded flame symbol is engraved near the broken blade.",
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
                    print(self.look(target, player))
            elif command in ["get", "take"]:
                print(self.get(target, player))
            elif command in ["drop", "put"]:
                print(self.drop(target, player))
            elif command == "use":
                print(self.use(target, player))
            elif command == "inventory":
                player.show_inventory()
            elif command == "stats":
                player.print_stats()
            elif command in ["help", "?"]:
                print(self.help_text())
            elif command == "hint":
                print(self.hint())
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

    def look(self, target, player):
        for obj in self.objects:
            if self.matches(obj, target) and obj.visible:
                if obj.name == "Ancient Ashes":
                    ember = self.find_object(self.objects, "Ancient Ember")
                    if ember is not None and not ember.visible:
                        ember.visible = True
                        return "You find a hidden ember in the ashes."
                return self.object_description(obj)
        for obj in player.inventory:
            if self.matches(obj, target):
                return self.object_description(obj)
        return "There is nothing like " + target + " to look at."

    def matches(self, obj, target):
        target = target.lower().strip()
        name = obj.name.lower()
        return target == name or target in name.split()

    def find_object(self, objects, target):
        for obj in objects:
            if self.matches(obj, target):
                return obj
        return None

    def object_description(self, obj):
        if obj.state is not None:
            return obj.description + "\nThe " + obj.name + " is " + obj.state + "."
        return obj.description

    def get(self, item_name, player):
        obj = self.find_object(self.objects, item_name)
        if obj is None or not obj.visible:
            return item_name + " is not here."
        if not obj.can_be_gotten:
            return "The " + obj.name + " cannot be taken."
        player.inventory.append(obj)
        self.objects.remove(obj)
        return "You take the " + obj.name + "."

    def drop(self, item_name, player):
        obj = self.find_object(player.inventory, item_name)
        if obj is None:
            return "You don't have the " + item_name + "."
        player.inventory.remove(obj)
        self.objects.append(obj)
        return "You drop the " + obj.name + "."

    def use(self, target, player):
        parts = target.lower().split(" on ", 1)
        item_name = parts[0].strip()

        if item_name not in ["ember", "ancient ember"]:
            return "You can't use that here."
        if len(parts) == 2 and parts[1].strip() not in [
            "bonfire",
            "dying bonfire",
            "the bonfire",
            "the dying bonfire",
        ]:
            return "That cannot be used there."

        ember = player.get_item("Ancient Ember")
        if ember is None:
            return "You need an ember to light the bonfire."
        if self.objects[0].state == "lit":
            return "The bonfire is already lit."

        self.objects[0].use()
        player.inventory.remove(ember)
        return "The ember catches. The bonfire is lit."

    def hint(self):
        return "The tombstone mentions an ember. Search the ashes, then light the bonfire to open the exits."

    def help_text(self):
        return (
            "Commands: go, move, look, get, take, drop, put, use, inventory, "
            "stats, help, ?, hint, quit\n"
            "Exits: " + ", ".join(self.exits)
        )

    def move(self, direction):
        direction = {"e": "east", "u": "up"}.get(direction, direction)
        if direction in self.exits:
            if self.objects[0].state != "lit":
                print("You must light the bonfire before you can leave.")
                return None
            return direction
        print("You can't go that way.")
        return None
