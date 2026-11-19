from object import Object
from player import Player


# A rope the player can pick up in this room.
# Like the Lamp in Room0, it inherits from Object and implements use().
class Rope(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        # Call the Object constructor so all the normal attributes get set.
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        # The rope does not do anything special when used; it just prints a message.
        # Its real job is to make climbing down the shaft safe (see Room.move).
        print("You coil the rope over your shoulder. It looks strong enough to climb down with.")


class Room:
    """
    Room 11 - The Forgotten Cistern (austin_rager)

    Exits (from map.txt):
      - north: a rusted iron door to Room 17. It is locked until the word lock is solved.
      - up:    a spiral staircase to Room 2. It is always open.
      - down:  a dark shaft to Room 5. Climbing down without a rope hurts
               (-20 health and the "bruised" condition). With a rope it is safe.

    Light:
      - The room is pitch black unless a lamp with state "on" is in the player's
        inventory or lying in the room. While dark the player cannot read the
        tablet, guess, or look at room features, but can still move and look at
        items they are carrying.

    Puzzle (Wordle-style word lock on the north door):
      - A stone tablet shows 3 riddles, one at a time. Each answer is a
        five-letter word. The player types "guess <word>".
      - Each guess is scored letter by letter:
          G = right letter in the right spot
          Y = right letter in the wrong spot
          - = letter not in the word
      - 6 guesses per riddle. A guess that is not exactly 5 letters is rejected
        and does not use a guess.
      - Correct answer: +10 score and the next riddle appears.
        After the 3rd riddle the door unlocks and the player gets a +15 bonus.
      - Running out of guesses: the tablet shocks the player for 10 health
        (health never drops below 1) and the same riddle starts over.
        Riddles already solved stay solved.
    """

    # Class constants so the numbers are easy to find and change.
    FALL_DAMAGE = 20        # health lost when falling down the shaft without a rope
    SHOCK_DAMAGE = 10       # health lost when all guesses on a riddle are used up
    MAX_ATTEMPTS = 6        # guesses allowed per riddle
    SCORE_PER_RIDDLE = 10   # score for each solved riddle
    SCORE_DOOR_BONUS = 15   # extra score for opening the door

    def __init__(self):
        self.room_num = 11
        # The door sentence is changed in guess() once the door opens.
        self.description = (
            "The Forgotten Cistern\n"
            "You stand in a dry, round stone chamber that once held water.\n"
            "To the north is a rusted iron door, shut tight. A stone tablet\n"
            "covered in runes is set into the wall beside it.\n"
            "A spiral staircase leads up through the ceiling.\n"
            "A dark shaft in the floor leads down into the depths."
        )
        self.exits = ["north", "up", "down"]
        self.objects = []
        rope = Rope("Rope", "A long, sturdy rope of braided hemp.", True, None, True)
        self.objects.append(rope)

        # The three riddles, in order. Each one has the answer word and a clue.
        self.puzzles = [
            {"word": "water", "clue": "I once filled this cistern to the brim."},
            {"word": "stone", "clue": "The walls, the floor and the ceiling are all made of me."},
            {"word": "flame", "clue": "I flicker inside your lamp and I chase the darkness away."},
        ]

        # Puzzle state.
        self.door_locked = True     # the north door starts locked
        self.current_puzzle = 0     # index into self.puzzles of the riddle being solved
        self.attempts = 0           # guesses used on the current riddle
        self.history = []           # list of (guess, marks) for the current riddle

    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room(player)

        while True:
            command = input("> ").lower().strip()
            if command == "":
                continue

            parts = command.split(" ", 1)
            command_base = parts[0]
            if len(parts) > 1:
                other_part = parts[1].strip()
            else:
                other_part = ""

            if command_base in ["go", "move"]:
                next_direction = self.move(other_part, player)
                if next_direction != None:
                    return next_direction

            elif command_base == "look":
                self.look(other_part, player)

            elif command_base == "read":
                self.read(other_part, player)

            elif command_base == "guess":
                self.guess(other_part, player)

            elif command_base == "use":
                self.use(other_part, player)

            elif command_base in ["get", "take"]:
                self.get(other_part, player)

            elif command_base in ["drop", "put"]:
                self.drop(other_part, player)

            elif command_base == "inventory":
                self.show_inventory(player)

            elif command_base == "stats":
                self.show_stats(player)

            elif command_base in ["help", "?"]:
                self.show_help()

            elif command_base == "hint":
                self.show_hint(player)

            elif command_base == "quit":
                if self.quit_game(player) == "quit":
                    return "quit"

            else:
                self.unknown_command()

    # Light helpers

    def is_lit(self, player):
        for item in player.inventory:
            if item.name.lower() == "lamp" and item.state == "on":
                return True
        for item in self.objects:
            if item.name.lower() == "lamp" and item.state == "on":
                return True
        return False

    def too_dark(self):
        # One message used everywhere the player tries to see in the dark.
        print("It's too dark to see that. You need a light.")

    # Command helpers

    def describe_room(self, player):
        # In the dark the player sees nothing.
        if not self.is_lit(player):
            print("It is pitch black. You can't see anything without a light.")
            return
        print(self.description)
        # List the objects lying in the room, skipping hidden ones.
        for obj in self.objects:
            if obj.visible:
                print(f"There is a {obj.name} here.")

    def move(self, direction, player):
        # Turn the aliases into the real direction names.
        if direction in ["north", "n", "door", "iron door"]:
            direction = "north"
        elif direction in ["up", "u", "stairs", "staircase"]:
            direction = "up"
        elif direction in ["down", "d", "shaft", "hole"]:
            direction = "down"

        if direction == "north":
            # The door stays shut until all three riddles are solved.
            if self.door_locked:
                print("The iron door is locked tight. The runes on the tablet seem to be the key.")
                return None
            print("You step through the open iron door.")
            return "north"

        if direction == "up":
            print("You climb the spiral staircase.")
            return "up"

        if direction == "down":
            if player.has_item("rope"):
                # With a rope the climb is safe.
                print("You tie off the rope and climb safely down the shaft.")
            else:
                # Without a rope the player falls and gets hurt.
                player.health -= self.FALL_DAMAGE
                # player.condition is a list, so only add "bruised" once.
                if "bruised" not in player.condition:
                    player.condition.append("bruised")
                print(f"You slip and fall down the shaft! You lose {self.FALL_DAMAGE} health and you are bruised.")
            return "down"

        # Anything else (including an empty direction) is not allowed.
        print("You can't go that way.")
        return None

    def look(self, target, player):
        # "look" with nothing after it reprints the room description.
        if target == "":
            self.describe_room(player)
            return

        # Items the player is carrying can be looked at even in the dark.
        item = self.get_item_from_inventory(target, player)
        if item != None:
            self.print_item(item)
            return

        # Everything else needs light.
        if not self.is_lit(player):
            self.too_dark()
            return

        # Room features.
        if target in ["door", "iron door"]:
            if self.door_locked:
                print("A heavy iron door, red with rust. It has no handle or keyhole, only the rune tablet beside it.")
            else:
                print("The rusted iron door stands open to the north.")
            return

        if target in ["stairs", "staircase"]:
            print("Worn stone steps spiral up through a hole in the ceiling.")
            return

        if target in ["shaft", "hole"]:
            print("A narrow shaft drops into darkness. Climbing down without a rope looks dangerous.")
            return

        if target in ["floor", "flagstones"]:
            print("Dusty flagstones, dry and cracked. A dark shaft opens in the middle of them.")
            return

        if target in ["tablet", "runes"]:
            self.show_tablet()
            return

        # Visible objects lying in the room.
        item = self.get_item_from_object_list(target)
        if item != None:
            self.print_item(item)
            return

        print("There is nothing like " + target + " to look at.")

    def print_item(self, item):
        # Print an item's description, plus its state if it has one.
        print(item.description)
        if item.state != None:
            print(f"The {item.name} is {item.state}.")

    def read(self, target, player):
        # Only the tablet (or its runes) can be read.
        if target not in ["tablet", "runes"]:
            print("There is nothing like that to read.")
            return
        if not self.is_lit(player):
            self.too_dark()
            return
        self.show_tablet()

    def show_tablet(self):
        # After the last riddle the tablet has nothing more to say.
        if not self.door_locked:
            print("The runes on the tablet have gone dark. The door is already open.")
            return

        puzzle = self.puzzles[self.current_puzzle]
        print(f"Riddle {self.current_puzzle + 1} of {len(self.puzzles)}: {puzzle['clue']}")
        print("The answer is a five-letter word. Type: guess <word>")
        print("Legend: G = right letter, right spot   Y = right letter, wrong spot   - = not in the word")
        print(f"Guesses left: {self.MAX_ATTEMPTS - self.attempts}")
        # Show every guess made on this riddle so far.
        for past_guess, marks in self.history:
            self.print_guess(past_guess, marks)

    def print_guess(self, word, marks):
        # Example output: "  S T A R E   - Y Y Y Y"
        print("  " + " ".join(word.upper()) + "   " + " ".join(marks))

    @staticmethod
    def score_guess(guess, answer):
        # Two-pass Wordle scoring so repeated letters are handled correctly.
        marks = ["-", "-", "-", "-", "-"]
        leftover = []  # answer letters that were not exact matches

        # Pass 1: exact matches get "G". Collect the unmatched answer letters.
        for i in range(5):
            if guess[i] == answer[i]:
                marks[i] = "G"
            else:
                leftover.append(answer[i])

        # Pass 2: a non-green guess letter that is still in leftover gets "Y".
        # Remove it from leftover so each answer letter is only used once.
        for i in range(5):
            if marks[i] != "G" and guess[i] in leftover:
                marks[i] = "Y"
                leftover.remove(guess[i])

        return marks

    def guess(self, word, player):
        if not self.door_locked:
            print("The tablet is silent. The door is already open.")
            return

        # The player has to be able to see the tablet.
        if not self.is_lit(player):
            self.too_dark()
            return

        # Reject anything that is not exactly five letters. This does not use a guess.
        if len(word) != 5 or not word.isalpha():
            print("The tablet only accepts five-letter words.")
            return

        # Score the guess and remember it.
        answer = self.puzzles[self.current_puzzle]["word"]
        marks = self.score_guess(word, answer)
        self.attempts += 1
        self.history.append((word, marks))
        self.print_guess(word, marks)
        print(f"Guesses left: {self.MAX_ATTEMPTS - self.attempts}")

        if word == answer:
            # Correct: give points and move to the next riddle.
            player.score += self.SCORE_PER_RIDDLE
            print(f"The runes flash green! (+{self.SCORE_PER_RIDDLE} score)")
            self.current_puzzle += 1
            self.attempts = 0
            self.history = []

            if self.current_puzzle == len(self.puzzles):
                # That was the last riddle: open the door.
                self.door_locked = False
                # Update the room description so it shows the door as open.
                self.description = (
                    "The Forgotten Cistern\n"
                    "You stand in a dry, round stone chamber that once held water.\n"
                    "To the north the rusted iron door stands open. The stone tablet\n"
                    "beside it has gone quiet.\n"
                    "A spiral staircase leads up through the ceiling.\n"
                    "A dark shaft in the floor leads down into the depths."
                )
                player.score += self.SCORE_DOOR_BONUS
                print(f"With a deep rumble, the rusted iron door grinds open to the north! (+{self.SCORE_DOOR_BONUS} bonus score)")
            else:
                # Show the next riddle.
                self.show_tablet()

        elif self.attempts >= self.MAX_ATTEMPTS:
            # Out of guesses: shock the player but never drop health below 1.
            player.health = max(1, player.health - self.SHOCK_DAMAGE)
            print(f"The tablet crackles and shocks you! You lose {self.SHOCK_DAMAGE} health.")
            print("The runes fade and the same riddle appears again.")
            self.attempts = 0
            self.history = []
            self.show_tablet()

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            item = self.get_item_from_object_list(item_name)
        if item == None:
            print("You can't use that.")
            return

        was_lit = self.is_lit(player)
        item.use()

        if not was_lit and self.is_lit(player):
            self.describe_room(player)

    def get(self, item_name, player):
        if player.has_item(item_name):
            print(f"You already have the {item_name}.")
            return

        item = self.get_item_from_object_list(item_name)
        if item == None:
            print(f"{item_name} is not here.")
            return

        if not item.can_be_gotten:
            print(f"The {item.name} cannot be taken.")
            return

        self.objects.remove(item)
        player.inventory.append(item)
        print(f"You take the {item.name} and add it to your inventory.")

    def drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name, player)
        if item == None:
            print(f"You don't have the {item_name}.")
            return

        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def show_inventory(self, player):
        player.show_inventory()

    def show_stats(self, player):
        player.print_stats()

    def show_help(self):
        print("Commands: go/move <direction>, look [thing], get/take <item>, drop/put <item>,")
        print("          use <item>, read tablet, guess <word>, inventory, stats, help/?, hint, quit")
        print("Exits: north (iron door), up (staircase), down (shaft)")

    def show_hint(self, player):
        # The hint depends on how far the player has gotten.
        lamp = self.get_item_from_inventory("lamp", player)
        if lamp == None:
            print("It's too dark to do much here. Did you pick up the lamp in the first room?")
        elif lamp.state != "on":
            print("Your lamp is off. Try: use lamp")
        elif self.door_locked:
            print("Read the tablet, then type 'guess <word>' with a five-letter answer to the riddle.")
        else:
            print("The north door is open. If you go down the shaft, a rope would make the climb safer.")

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().startswith("y"):
            player.print_stats()
            return "quit"
        return None

    def unknown_command(self):
        print("You can't do that here. Type 'help' for options or 'hint' for a clue.")

    # Item lookup helpers (case-insensitive)

    def get_item_from_inventory(self, item_name, player):
        for item in player.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def get_item_from_object_list(self, item_name):
        # Hidden objects (visible=False) can't be found, looked at or taken.
        for item in self.objects:
            if item.name.lower() == item_name.lower() and item.visible:
                return item
        return None
