from object import Object
from player import Player


# The README requires every room to create at least one Object the player can pick up.
class Pebble(Object):
    def __init__(self):
        super().__init__("pebble", "A small, smooth pebble.", True, None, True)

    def use(self):
        print("You toss the pebble from hand to hand. Riveting.")


class Room:

    # What the narrator says each time the player tries to enter the hole.
    # Attempt 1 prints line 0, attempt 2 prints line 1, and so on.
    NARRATOR_LINES = [
        "Narrator: That's just a hole. Ignore it. There are perfectly good exits elsewhere.",
        "Narrator: No, really. It's a hole. Nothing in there for you. Pick another room.",
        "Narrator: I can see you leaning over the edge. Please stop leaning over the edge.",
        "Narrator: I've been narrating this dungeon for three hundred years. Trust me. Leave the hole alone.",
        "Narrator: Do you know how much paperwork it is when an adventurer falls in a hole? A lot.",
        "Narrator: ...Fine. FINE. You know what? Do it. See if I care.",
    ]

    def __init__(self):
        self.room_num = 14
        self.exits = ["south", "west", "up", "down"]
        self.objects = [Pebble()]          # per-room list (not shared between rooms)
        self.hole_attempts = 0             # how many times the player has tried the hole

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room()

        while True:
            command = input("> ")
            result = self.process_command(command, player)
            if result is not None:
                return result

    def process_command(self, command, player):
        """Handle one command. Returns a direction, "quit", or None to stay in the room."""
        parts = command.lower().strip().split(maxsplit=1)
        if not parts:
            return None
        verb = parts[0]
        target = parts[1] if len(parts) > 1 else ""

        # Anything that sounds like "get into the hole" goes to try_hole()
        if verb in ["enter", "jump", "climb", "go", "move"] and "hole" in target:
            return self.try_hole(player)

        if verb in ["go", "move"]:
            return self.move(target)
        elif verb == "look":
            self.look(target, player)
        elif verb in ["get", "take"]:
            self.get(target, player)
        elif verb == "drop":
            self.drop(target, player)
        elif verb == "use":
            self.use(target, player)
        elif verb == "inventory":
            player.show_inventory()
        elif verb == "stats":
            player.print_stats()
        elif verb in ["help", "?"]:
            self.show_help()
        elif verb == "hint":
            print("Narrator: Hint: don't go in the hole.")
        elif verb == "quit":
            return self.quit_game(player)
        else:
            print("You can't do that here. Type 'help' for commands.")
        return None

    # ------------------------------------------------------------------
    # The hole
    # ------------------------------------------------------------------
    def try_hole(self, player):
        self.hole_attempts += 1

        # Attempts 1-6: the narrator talks the player out of it.
        if self.hole_attempts <= len(self.NARRATOR_LINES):
            print(self.NARRATOR_LINES[self.hole_attempts - 1])
            return None

        # Attempt 7: the player jumps, gets stuck, and dies.
        print("You jump into the hole.")
        print("It is narrower than it looked. Much narrower.")
        print("You are now stuck. Upside down. Forever.")
        print("Narrator: I told you so. Six times, actually.")
        player.health = 0
        player.condition.append("stuck in a hole")

        # Adventure.py checks player.is_alive() right after the room returns,
        # so returning any valid exit ends the game before the next room starts.
        return "down"

    # ------------------------------------------------------------------
    # Standard commands
    # ------------------------------------------------------------------
    def describe_room(self):
        print("You are in a plain stone room. In the center of the floor is a big, dark hole.")
        print("An archway leads WEST, a corridor runs SOUTH, a ladder climbs UP,")
        print("and a stone staircase in the corner spirals DOWN.")
        for obj in self.objects:
            print(f"You see a {obj.name} here.")

    def move(self, direction):
        moves = {
            "south": "You walk down the corridor to the south.",
            "west": "You step through the archway to the west.",
            "up": "You climb the ladder.",
            "down": "You take the staircase down. (Not the hole. Good choice.)",
        }
        short = {"s": "south", "w": "west", "u": "up", "d": "down"}
        direction = short.get(direction, direction)

        if direction in moves:
            print(moves[direction])
            return direction
        print("You can't go that way.")
        return None

    def look(self, target, player):
        if target == "":
            self.describe_room()
        elif target == "hole":
            print("Narrator: It's a hole. It's dark. Stop looking at it.")
        else:
            item = player.get_item(target) or self.find_in_room(target)
            if item is None:
                print(f"There is nothing like {target} to look at.")
            else:
                print(item.description)

    def get(self, target, player):
        item = self.find_in_room(target)
        if item is None:
            print(f"There is no {target} here.")
        elif not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
        else:
            self.objects.remove(item)
            player.inventory.append(item)
            print(f"You take the {item.name}.")

    def drop(self, target, player):
        item = player.get_item(target)
        if item is None:
            print(f"You don't have a {target}.")
        else:
            player.inventory.remove(item)
            self.objects.append(item)
            print(f"You drop the {item.name}.")

    def use(self, target, player):
        item = player.get_item(target) or self.find_in_room(target)
        if item is None:
            print("You can't use that.")
        else:
            item.use()

    def find_in_room(self, name):
        for obj in self.objects:
            if obj.name.lower() == name.lower():
                return obj
        return None

    def show_help(self):
        print("Commands: go/move <direction>, look [thing], get/take, drop, use,")
        print("          inventory, stats, hint, help/?, quit")
        print("Exits: " + ", ".join(self.exits))

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith("y"):
            player.print_stats()
            return "quit"
        return None
