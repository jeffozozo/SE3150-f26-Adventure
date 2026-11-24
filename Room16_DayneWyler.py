class Room:
    def __init__(self):
        self.room_num = 16
        self.description = (
            "You stand in an abandoned minecart junction. Four battered minecarts wait on separate "
            "tracks radiating from a central stone turntable:\n"
            "  - North: A plain cart facing a lantern-lit tunnel that fades into crushing darkness.\n"
            "  - South: An over-grown cart facing a deep, echoing cavern.\n"
            "  - West:  A gilded cart facing a narrow, crystal-lined rock passage.\n"
            "  - East:  A heavily damaged cart facing a collapsed rockfall.\n\n"
            "In the center of the room stands a heavy stone switchboard with three sliding grooves "
            "and three engraved stones resting in a trough beside it."
        )
        self.exits = ['north', 'west', 'east', 'south']
        self.objects = []

        # Puzzle State: 3 slots on the switchboard (None = empty)
        self.slots = [None, None, None]
        self.trough = ['gold', 'moss', 'iron']

    def get_unlocked_cart(self):
        """Evaluates the current slot positions and returns which cart is unlocked."""
        if self.slots == ['iron', None, None]:
            return "plain"
        elif self.slots == [None, 'moss', None]:
            return "over-grown"
        elif self.slots == [None, None, 'gold']:
            return "gilded"
        elif self.slots == ['iron', 'gold', 'moss']:
            return "heavily damaged"
        return None

    def render_switchboard(self):
        """Renders the current state of the sliding stones puzzle in ASCII art."""
        def fmt(val):
            return {"gold": "[ G ]", "moss": "[ M ]", "iron": "[ I ]"}.get(val, "[ . ]")

        s1, s2, s3 = fmt(self.slots[0]), fmt(self.slots[1]), fmt(self.slots[2])
        trough_str = " ".join(fmt(s) for s in self.trough) if self.trough else "(empty)"
        unlocked = self.get_unlocked_cart()
        status = f"UNLOCKED: {unlocked.upper()} CART" if unlocked else "ALL WHEEL-LOCKS ENGAGED"

        print(f"""
        === JUNCTION SWITCHBOARD ===
             (N)          (W)
              |            |
         Slot 1       Slot 3
          {s1}--------{s3}
               \\      /
                \\    /
                 {s2}  <-- Slot 2
                  |
                 (S)

        Trough: {trough_str}
        Key: [I]ron = North | [M]oss = South | [G]old = West
        Status: {status}
        ============================
        """)

    def enter(self, player):
        player.current_room = self.room_num
        self.describe_room()
        self.render_switchboard()

        while True:
            parts = input("> ").lower().split(maxsplit=1)
            if not parts:
                continue
            command = parts[0]
            target = parts[1].strip() if len(parts) > 1 else ""

            if command in ["go", "move"]:
                print(
                    "The tracks drop steeply into the dark. Walking is impossible—"
                    "you'll have to unlock and ride one of the minecarts."
                )

            elif command in ["slide", "place", "put"]:
                self.handle_slide(target)

            elif command in ["remove", "take", "pull"]:
                self.handle_remove(target)

            elif command == "reset":
                self.slots = [None, None, None]
                self.trough = ['gold', 'moss', 'iron']
                print("You slide all the stones back into the trough. Heavy iron clamps snap shut on all four carts.")
                self.render_switchboard()

            elif command in ["ride", "board"]:
                cart = self.ride(target, player)
                if cart is not None:
                    return cart

            elif command == "look":
                self.handle_look(target)

            elif command == "inventory":
                player.show_inventory()

            elif command == "stats":
                player.print_stats()

            elif command in ["help", "?"]:
                print(
                    "Commands:\n"
                    "  look [target]          - Inspect room, switchboard, or carts\n"
                    "  slide [stone] [1/2/3]  - Slide a stone (gold, moss, iron) into a slot\n"
                    "  remove [1/2/3]         - Slide a stone from a slot back to the trough\n"
                    "  reset                  - Return all stones to the trough\n"
                    "  ride [cart name]       - Board an unlocked minecart\n"
                    "  inventory / stats / hint / quit"
                )

            elif command == "hint":
                print(
                    "Align a single stone with its matching slot to unlock its cart:\n"
                    "  - Slot 1 points North (Iron)\n"
                    "  - Slot 2 points South (Moss)\n"
                    "  - Slot 3 points West (Gold)\n"
                    "Try 'slide iron 1' to unlock the plain cart."
                )

            elif command == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
            else:
                print("Command unavailable. Type 'help' for puzzle commands.")

    def handle_slide(self, target):
        words = [w for w in target.replace("slot", "").replace("into", "").replace("to", "").split()]
        if len(words) < 2:
            print("Specify a stone and a slot number (1, 2, or 3). Example: 'slide gold 3'")
            return

        stone_map = {"g": "gold", "gold": "gold", "m": "moss", "moss": "moss", "i": "iron", "iron": "iron"}
        stone = stone_map.get(words[0])
        slot_input = words[1]

        if not stone:
            print("Invalid stone. Choose 'gold', 'moss', or 'iron'.")
            return
        if slot_input not in ["1", "2", "3"]:
            print("Invalid slot. Choose slot 1, 2, or 3.")
            return

        idx = int(slot_input) - 1

        # Remove the moving stone from its current location
        if stone in self.trough:
            self.trough.remove(stone)
        elif stone in self.slots:
            self.slots[self.slots.index(stone)] = None

        # If target slot already has a stone, return it to the trough automatically
        displaced = self.slots[idx]
        if displaced is not None:
            self.trough.append(displaced)
            print(f"You slide the {displaced} stone out of Slot {slot_input} and replace it with the {stone} stone.")
        else:
            print(f"You grind the {stone} stone into Slot {slot_input} with a heavy *CLUNK*.")

        self.slots[idx] = stone

        unlocked = self.get_unlocked_cart()
        if unlocked:
            print(f"Mechanisms whir beneath the floorboards! The wheel-clamp on the {unlocked.upper()} CART releases!")
        else:
            print("The gears shift, but all wheel-clamps remain locked.")

        self.render_switchboard()

    def handle_remove(self, target):
        slot_input = target.replace("slot", "").strip()
        if slot_input not in ["1", "2", "3"]:
            print("Specify which slot to clear (1, 2, or 3). Example: 'remove 1'")
            return
        idx = int(slot_input) - 1
        stone = self.slots[idx]
        if stone is None:
            print(f"Slot {slot_input} is already empty.")
            return
        self.slots[idx] = None
        self.trough.append(stone)
        print(f"You slide the {stone} stone out of Slot {slot_input} and back into the trough.")
        self.render_switchboard()

    def handle_look(self, target):
        if not target:
            self.describe_room()
            self.render_switchboard()
        elif target in ["switchboard", "board", "stones", "puzzle", "turntable"]:
            self.render_switchboard()
            print(
                "Faintly chiseled into the stone base is a warning:\n"
                "'ONE STONE ALIGNS ONE PATH. ALL THREE ALIGN THE FORGOTTEN TRACK.'"
            )
        elif target in ["gilded cart", "gold cart", "gilded minecart", "gold minecart", "gilded"]:
            state = "UNLOCKED" if self.get_unlocked_cart() == "gilded" else "LOCKED by a thick iron wheel-clamp"
            print(f"A pristine, gold-covered minecart on well-maintained west-bound tracks. It is currently {state}.")
        elif target in ["plain cart", "basic cart", "plain minecart", "basic minecart", "plain"]:
            state = "UNLOCKED" if self.get_unlocked_cart() == "plain" else "LOCKED by a thick iron wheel-clamp"
            print(f"A dirty, sturdy minecart sitting on the north-bound track. It is currently {state}.")
        elif target in ["heavily damaged cart", "damaged cart", "damaged"]:
            state = "UNLOCKED" if self.get_unlocked_cart() == "heavily damaged" else "LOCKED by a rusted wheel-clamp"
            print(f"A heavily dented minecart facing the east rockfall. Scratched into its side are the letters: 'I - G - M'. It is currently {state}.")
        elif target in ["over-grown cart", "overgrown cart", "overgrown minecart", "over-grown minecart", "overgrown"]:
            state = "UNLOCKED" if self.get_unlocked_cart() == "over-grown" else "LOCKED by a thick iron wheel-clamp"
            print(f"A vine-choked cart on newly laid south-bound rails. It is currently {state}.")
        elif target in ["track", "tracks", "junction"]:
            print("Heavy iron linkages run beneath the floorboards from the central switchboard to each cart's wheel-clamp.")
        else:
            print("Nothing to describe.")

    def describe_room(self):
        print(self.description)
        print("Exits: " + ", ".join(self.exits))

    def ride(self, target, player):
        unlocked = self.get_unlocked_cart()

        # If player just types "ride" with no cart name, board the unlocked cart automatically
        if not target.strip():
            if unlocked:
                normalized_cart = unlocked
            else:
                print("All four minecarts are locked to the tracks. Align the switchboard stones first.")
                return None
        else:
            words = target.split()
            if words and words[0] in ["cart", "minecart"]:
                words = words[1:]
            choice = " ".join(words).strip()

            aliases = {
                "plain cart": "plain", "basic cart": "plain", "plain minecart": "plain", "plain": "plain",
                "heavily damaged cart": "heavily damaged", "damaged cart": "heavily damaged", "damaged": "heavily damaged", "heavily damaged": "heavily damaged",
                "gilded cart": "gilded", "gold cart": "gilded", "gilded minecart": "gilded", "gilded": "gilded",
                "over-grown cart": "over-grown", "overgrown cart": "over-grown", "overgrown": "over-grown", "over-grown": "over-grown",
            }
            normalized_cart = aliases.get(choice)

            if not normalized_cart:
                print("Choose one of the minecarts: gilded cart, plain cart, heavily damaged cart, or over-grown cart.")
                return None

            if normalized_cart != unlocked:
                print(
                    f"You climb into the {normalized_cart} cart and pull the brake lever, but the wheels don't budge! "
                    "A heavy iron clamp locks it to the track. You need to align the switchboard first."
                )
                return None

        cart_routes = {
            "plain": "north",
            "over-grown": "south",
            "gilded": "west",
            "heavily damaged": "east",
        }
        direction = cart_routes[normalized_cart]

        route_stories = {
            "north": (
                "The plain cart rattles past a row of old lanterns and climbs a steep slope. "
                "It bursts out of the tunnel toward the north before skittering to a stop near an empty room with a hole in the middle."
            ),
            "south": (
                "The over-grown cart swerves left and right until your stomach flips, hurtling straight toward a solid wall. "
                "Just before impact, hidden stone doors grind open to reveal a southern chamber."
            ),
            "west": (
                "The gilded cart plunges into a cavern, skimming past glittering crystals "
                "before slowing smoothly at the western passage."
            ),
            "east": (
                "The heavily damaged cart lurches forward and smashes straight through the loose east rockfall! "
                "Before you can celebrate, the rails end abruptly over a bottomless abyss. You plummet into the dark. You are dead."
            ),
        }

        print(route_stories[direction])
        if direction == "east":
            player.health = 0
            player.condition.append("stuck in the bottom of a hole.")
        return direction