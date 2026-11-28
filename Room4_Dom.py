import random
from object import Object


# The poses printed on the sign. Only these count as real attempts.
VALID_POSES = ["star", "flamingo", "pencil", "hourglass", "snake", "squat"]

# The walls, in the order they come at the player.
WALLS = [
    {
        "pose": "flamingo",
        "art": r"""
    #############
    ###  \O/  ###
    ###   |   ###
    ###   |\  ###
    ###   |   ###
    #############""",
    },
    {
        "pose": "hourglass",
        "art": r"""
    #############
    ### \___/ ###
    ###  \ /  ###
    ###   X   ###
    ###  / \  ###
    ### /___\ ###
    #############""",
    },
    {
        "pose": "snake",
        "art": r"""
    #############
    ###  ____ ###
    ### /     ###
    ### \___  ###
    ###     \ ###
    ### ____/ ###
    #############""",
    },
]

STEPS_PER_WALL = 3

SHERLOCK_LINES = {
    "entry": [
        "Sherlock: \"A visitor! I've been here 41 days. Or 41 years. Time is a social construct, Watson.\"",
    ],
    "correct": [
        "Sherlock: \"Elementary. I have failed that exact wall four hundred times.\"",
        "Sherlock: \"You make it look easy. What agency do you work for!? \"",
    ],
    "wrong": [
        "Sherlock: \"I deduced it was a triangle. Nothing is real.\"",
        "Sherlock: \"Welcome to my world. It is wet here.\"",
    ],
    "close": [
        "Sherlock: \"THE WALL KNOWS MY NAME.\"",
        "Sherlock: \"Pose! POSE! Why are you reading things?!\"",
    ],
    "locked": [
        "Sherlock: \"Champions only. I have never once been a champion.\"",
    ],
    "win": [
        "Sherlock: \"You did it! Take me with you! ...No? Fine. I'll just stay here. Forever.\"",
    ],
    "random": [
        "Sherlock: \"I used to solve murders. Now I can't solve a hole.\"",
        "Sherlock: \"Mrs. Hudson thinks I'm on holiday.\"",
        "Sherlock: \"I have deduced that the pool is 80% my tears.\"",
    ],
}


class MagnifyingGlass(Object):
    # state holds the index of the wall currently coming (0-2),
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        if self.state == 0:
            print("Sherlock squints through the glass: \"This hole looks some kind of bird.\"")
        elif self.state == 1:
            print("Sherlock squints through the glass: \"This hole makes you want to check the time\"")
        elif self.state == 2:
            print("Sherlock squints through the glass: \"This last hole looks like an S. Hiss.\"")
        elif self.state == len(WALLS):
            print("You got through all the holes, give yourself a pat on the back.")
        else:
            print("You inspect your own fingerprints. Riveting.")


class GoldenHoleTrophy(Object):
    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        print("You hold the trophy aloft. Somewhere, Chip Rumble applauds.")


class PropWall(Object):
    def __init__(self, name, description, state, visible):
        super().__init__(name, description, False, state, visible)

    def use(self):
        print("You lean on the prop wall. It's load-bearing, apparently.")


class Room:
    def __init__(self):
        self.room_num = 4
        self.description = (
            "Welcome to HOLE IN THE WALL! Studio lights blind you and a laugh track plays from nowhere.\n"
            "Game show host Chip Rumble grins at you with far too many teeth. Sherlock Holmes sits\n"
            "dripping at the edge of a pool, staring into the middle distance.\n"
            "A sign lists the official poses: " + ", ".join(VALID_POSES) + ".\n"
            "The only way forward is up the CHAMPIONS STAIRS, and you must win to climb them.\n"
            "A floor hatch beside the pool leads back down. Type 'play' when you're brave enough."
        )
        self.solved_description = (
            "Confetti covers the HOLE IN THE WALL set. The CHAMPIONS STAIRS glow, leading up.\n"
            "Chip Rumble is still clapping. Sherlock is weeping into the pool. The floor hatch leads down."
        )
        self.exits = ["up", "down"]

        self.glass = MagnifyingGlass(
            "magnifying glass", "Sherlock's magnifying glass. It's seen better days.", True, None, True
        )
        self.prop_wall = PropWall(
            "prop wall", "A spare foam wall with a hole shaped like a sad detective.", "standing", True
        )
        self.objects = [self.glass, self.prop_wall]

        self.walls_cleared = 0
        self.round_active = False
        self.steps_left = STEPS_PER_WALL
        self.solved = False
        self.sherlock_spoke = False

    # ---------- main loop ----------

    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room()
        self.sherlock("entry")
        while True:
            parts = input("> ").lower().split(maxsplit=1)
            if not parts:
                continue
            command = parts[0]
            target = parts[1].strip() if len(parts) > 1 else ""

            self.sherlock_spoke = False
            result = self.handle_command(command, target, player)
            if result is not None:
                return result
            if not self.sherlock_spoke:
                self.sherlock("random")

    def handle_command(self, command, target, player):
        """Runs one command. Returns a direction or "quit" to leave the room, otherwise None."""
        previous_round_started = self.round_active
        uses_step = True

        if command in ["go", "move"]:
            direction = self.move(target)
            if direction is not None:
                return direction
        elif command == "pose":
            return self.pose(target, player)
        elif command == "look":
            self.look(target, player)
        elif command in ["get", "take"]:
            self.get(target, player)
        elif command == "drop":
            self.drop(target, player)
        elif command == "use":
            item = self.use(target, player)
            if item is self.glass:
                uses_step = False  # the magnifying glass freezes time (sort of)
        elif command == "play":
            self.start_round()
        elif command == "talk":
            self.talk(target)
        elif command == "inventory":
            player.show_inventory()
        elif command == "stats":
            player.print_stats()
        elif command in ["help", "?"]:
            self.show_help()
        elif command == "hint":
            self.show_hint()
        elif command == "quit":
            if input("Are you sure? (y/n) ").lower().startswith("y"):
                player.print_stats()
                return "quit"
        else:
            print("Command unavailable.")

        # Every non-pose command during a round lets the wall move closer.
        if previous_round_started and self.round_active and uses_step:
            if self.tick(player):
                return "down"
        return None

    # ---------- the game ----------

    def start_round(self):
        if self.solved:
            print("Chip Rumble: \"You're already a champion! Head on up those stairs!\"")
            return
        if self.round_active:
            print("Chip Rumble: \"A wall is already coming at you, champ!\"")
            return
        self.round_active = True
        self.steps_left = STEPS_PER_WALL
        self.glass.state = self.walls_cleared
        print("Chip Rumble: \"LET'S PLAY HOLE IN THE WALL!\" The music swells.")
        self.draw_wall()

    def draw_wall(self):
        wall = WALLS[self.walls_cleared]
        print(f"Wall {self.walls_cleared + 1} of {len(WALLS)} rumbles toward you:")
        print(wall["art"])
        print(f"It is {self.steps_left} steps away. Type 'pose <name>'!")

    def pose(self, name, player):
        if not self.round_active:
            print("You strike a pose. Nobody is watching. Type 'play' to start.")
            return None

        if name not in VALID_POSES:
            print("That's not a pose on the sign. You flail awkwardly.")
            if self.tick(player):
                return "down"
            return None

        if name == WALLS[self.walls_cleared]["pose"]:
            self.walls_cleared += 1
            print("You slip through the hole! The crowd goes wild!")
            self.sherlock("correct")
            if self.walls_cleared == len(WALLS):
                self.win(player)
            else:
                self.steps_left = STEPS_PER_WALL
                self.glass.state = self.walls_cleared
                self.draw_wall()
            return None

        print("SPLAT. You did not fit. What a chump")
        self.sherlock("wrong")
        self.fail(player)
        return "down"

    def tick(self, player):
        """Moves the wall one step closer. Returns True if it hit the player."""
        self.steps_left -= 1
        if self.steps_left <= 0:
            print("The wall arrives. You were not in a pose. SPLAT.")
            self.fail(player)
            return True
        print(f"The wall is {self.steps_left} step{'s' if self.steps_left != 1 else ''} away...")
        if self.steps_left == 1:
            self.sherlock("close")
        return False

    def fail(self, player):
        player.health -= 10
        if "wet" not in player.condition:
            player.condition.append("wet")
        self.reset_round()
        print("The wall shoves you into the pool and you're flushed out through the floor hatch!")

    def win(self, player):
        self.solved = True
        self.round_active = False
        self.glass.state = len(WALLS)
        player.score += 50
        player.inventory.append(
            GoldenHoleTrophy("golden hole trophy", "A golden donut on a stick. You earned it.", True, "shiny", True)
        )
        self.description = self.solved_description
        print("Chip Rumble: \"WE HAVE A CHAMPION!\" He hands you the Golden Hole Trophy. (+50 score)")
        print("The CHAMPIONS STAIRS light up. The way up is open!")
        self.sherlock("win")

    def reset_round(self):
        self.walls_cleared = 0
        self.round_active = False
        self.steps_left = STEPS_PER_WALL
        self.glass.state = None

    # ---------- standard commands ----------

    def describe_room(self):
        print(self.description)
        print("Exits: " + ", ".join(self.visible_exits()))

    def visible_exits(self):
        return self.exits if self.solved else ["down"]

    def move(self, direction):
        direction = {"u": "up", "d": "down"}.get(direction, direction)
        if direction == "up" and not self.solved:
            print("A neon sign over the stairs reads CHAMPIONS ONLY.")
            self.sherlock("locked")
            return None
        if direction == "down" and self.round_active:
            print("You bail out through the floor hatch. Chip Rumble boos. Your progress is lost.")
            self.reset_round()
        if direction in self.exits:
            return direction
        print("You can't go that way.")
        return None

    def look(self, target, player):
        if not target:
            self.describe_room()
            if self.round_active:
                self.draw_wall()
        elif target == "sign":
            print("OFFICIAL POSES: " + ", ".join(VALID_POSES))
        elif target == "wall" and self.round_active:
            self.draw_wall()
        elif target in ["sherlock", "holmes", "sherlock holmes"]:
            print("The world's greatest detective, soaking wet and staring at his own reflection.")
        elif target in ["host", "chip", "chip rumble"]:
            print("Chip Rumble. Spray tan. Sparkly jacket. Thirty-four teeth.")
        else:
            item = self.find_item(target, self.objects) or self.find_item(target, player.inventory)
            if item:
                print(item.description)
            else:
                print("You don't see that here.")

    def get(self, target, player):
        item = self.find_item(target, self.objects)
        if item is None:
            if self.find_item(target, player.inventory):
                print("You already have that.")
            else:
                print("There's no " + target + " here." if target else "Get what?")
            return
        if not item.can_be_gotten:
            print("Chip Rumble slaps your hand. \"That's a set piece, champ.\"")
            return
        self.objects.remove(item)
        player.inventory.append(item)
        print("You take the " + item.name + ".")

    def drop(self, target, player):
        item = self.find_item(target, player.inventory)
        if item is None:
            print("You don't have that." if target else "Drop what?")
            return
        player.inventory.remove(item)
        self.objects.append(item)
        print("You drop the " + item.name + ".")

    def use(self, target, player):
        """Uses an item from the inventory or the room. Returns the item used, or None."""
        item = self.find_item(target, player.inventory) or self.find_item(target, self.objects)
        if item is None:
            print("You don't have that." if target else "Use what?")
            return None
        item.use()
        return item

    def talk(self, target):
        if target in ["sherlock", "holmes", "sherlock holmes"]:
            self.sherlock("random")
        elif target in ["host", "chip", "chip rumble"]:
            self.start_round()
        else:
            print("Talk to whom? Try 'talk sherlock' or 'talk host'.")

    def show_help(self):
        print("Commands: go/move <dir>, look [item], get/take <item>, drop <item>, use <item>,")
        print("          play, pose <name>, talk <sherlock|host>, inventory, stats, help, hint, quit")
        print("Poses: " + ", ".join(VALID_POSES))
        print("Exits: " + ", ".join(self.visible_exits()))

    def show_hint(self):
        if self.solved:
            print("Sherlock: \"Go up, champion. Leave me to my puddle.\"")
        elif self.round_active:
            print("Sherlock: \"Observe the hole. Match the shape to a pose on the sign. A magnifying glass helps... I'm told.\"")
        else:
            print("Sherlock: \"Type 'play' to face the wall. Pick up my magnifying glass first. Trust me.\"")
        self.sherlock_spoke = True

    def sherlock(self, situation):
        print(random.choice(SHERLOCK_LINES[situation]))
        self.sherlock_spoke = True

    @staticmethod
    def find_item(name, items):
        if not name:
            return None
        for item in items:
            item_name = item.name.lower()
            if name == item_name or item_name.endswith(" " + name):
                return item
        return None
