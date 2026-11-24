from object import Object
from player import Player

class ThrowingStone(Object):

    def __init__(self, name, description, can_be_gotten, state, visible):
        super().__init__(name, description, can_be_gotten, state, visible)

    def use(self):
        if self.state == "carried":
            print(
                f"You weigh the {self.name} in your hand. It's the right size for throwing"
            )
        elif self.state == "thrown":
            print(f"You already threw the {self.name}.")
        else:
            print(f"You'll need to pick up the {self.name} before you can use it.")

    def __str__(self):
        return self.name
        
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
            "and three engraved artifacts resting in a trough beside it."
        )
        self.exits = ['north', 'west', 'east', 'south']

        # 5 distinct throwing stone Object instances available to pick up in the room
        self.objects = [
            ThrowingStone("flint", "A sharp-edged chunk of dark flint", True, "on_ground", True),
            ThrowingStone("granite", "A dense, speckled lump of granite", True, "on_ground", True),
            ThrowingStone("quartz", "A cloudy white chunk of quartz that catches the dim lantern light.", True, "on_ground", True),
            ThrowingStone("slate", "A flat, smooth disc of slate", True, "on_ground", True),
            ThrowingStone("pumice", "A hollow, light rock that seems to have been purposefully placed here.", True, "on_ground", True),
        ]
        self.throwing_stone_names = {stone.name for stone in self.objects}

        # Switchboard puzzle state
        self.empty = "[ .... ]"
        self.slots = [self.empty, self.empty, self.empty]
        self.trough = ["[ gold ]", "[ moss ]", "[ iron ]"]

    def get_unlocked_cart(self):
        """Evaluates the current slot positions and returns which cart is unlocked."""
        if self.slots == ["[ iron ]", self.empty, self.empty]:
            return "plain"
        elif self.slots == [self.empty, "[ moss ]", self.empty]:
            return "over-grown"
        elif self.slots == [self.empty, self.empty, "[ gold ]"]:
            return "gilded"
        elif self.slots.count(self.empty) < 3:
            # There is at least one non-artifact in the slots
            return "heavily damaged"
        return None

    def render_switchboard(self):
        """Renders the current state of the sliding stones puzzle in ASCII art."""
        s1, s2, s3 = self.slots
        trough_str = " ".join(self.trough) if self.trough else "(empty)"
        unlocked = self.get_unlocked_cart()
        status = f"UNLOCKED: {unlocked.upper()} CART" if unlocked else "ALL WHEEL-LOCKS ENGAGED"

        print(f"""
        === JUNCTION SWITCHBOARD ===
              (N)              (W)
               |                |
           Slot 1            Slot 3
          {s1}----------{s3}
                 \\        /
                  \\      /
                  {s2}  <-- Slot 2
                     |
                    (S)

        Trough: {trough_str}
        Key: [ iron ] = North | [ moss ] = South | [ gold ] = West
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

            elif command in ["remove", "pull"]:
                self.handle_remove(target)

            elif command in ["take", "grab", "get", "pickup"]:
                if target.replace("slot", "").strip() in ["1", "2", "3"]:
                    self.handle_remove(target)
                else:
                    self.handle_take(target, player)

            elif command == "use":
                self.use(target, player)

            elif command == "reset":
                self.slots = [self.empty, self.empty, self.empty]
                self.trough = ["[ gold ]", "[ moss ]", "[ iron ]"]
                print("You slide all the artifacts back into the trough. Heavy iron clamps snap shut on all four carts.")
                self.render_switchboard()

            elif command in ["ride", "board"]:
                cart = self.ride(target, player)
                if cart is not None:
                    return cart
            
            elif command == "drop":
                self.handle_drop(target, player)

            elif command == "look":
                self.handle_look(target, player)

            elif command == "inventory":
                player.show_inventory()

            elif command == "stats":
                player.print_stats()

            elif command in ["help", "?"]:
                print(
                    "Commands:\n"
                    "  look [target]          - Inspect room, switchboard, stones, or carts\n"
                    "  take [stone/all]       - Pick up loose stones from the floor\n"
                    "  use [item]             - Use an item in your inventory\n"
                    "  slide [artifact] [1/2/3]  - Slide a switchboard artifact (gold, moss, iron) into a slot\n"
                    "  remove [1/2/3]         - Slide a switchboard artifact back to the trough\n"
                    "  reset                  - Return all switchboard stones to the trough\n"
                    "  ride [cart name]       - Board an unlocked minecart\n"
                    "  inventory / stats / hint / quit"
                )

            elif command == "hint":
                print(
                    "1. Align a single artifact with its matching slot to unlock its cart:\n"
                    "   - Slot 1 points North\n"
                    "   - Slot 2 points South\n"
                    "   - Slot 3 points West\n"
                    "2. You might want to grab some loose stones from the floor. You never know when you might need one."
                )

            elif command == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
            else:
                print("Command unavailable. Type 'help' for puzzle commands.")

    def use(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            item = self.get_item_from_object_list(item_name)
        
        #this room only allows you to use the objects in the list or inventory. That is not a global constraint however and you can add whatever use functions you like.
        if(item == None):
            print("you can't use that.")
            return
        
        item.use()

    def handle_take(self, target, player):
        available = [obj for obj in self.objects if obj.visible and obj.can_be_gotten]
        if not available:
            print("There are no loose stones left on the ground.")
            return

        if not target or target in ["stone", "rock", "a stone", "a rock"]:
            picked = available[0]
            self.objects.remove(picked)
            picked.state = "carried"
            player.inventory.append(picked)
            print(f"You pick up a piece of {picked.name} and put it in your inventory.")
            return

        if target in ["all", "stones", "all stones", "rocks", "all rocks"]:
            taken_names = []
            for obj in available:
                self.objects.remove(obj)
                obj.state = "carried"
                player.inventory.append(obj)
                taken_names.append(obj.name)
            print(f"You scoop up all the remaining stones ({', '.join(taken_names)}) and put them in your inventory.")
            return

        # Match a specific stone name (e.g., "flint" or "flint stone")
        cleaned = target.replace("stone", "").replace("rock", "").strip()
        match = next((obj for obj in available if obj.name.lower() == cleaned), None)
        if match:
            self.objects.remove(match)
            match.state = "carried"
            player.inventory.append(match)
            print(f"You pick up the {match.name} and put it in your inventory.")
        else:
            available_names = ", ".join(obj.name for obj in available)
            print(f"You don't see '{target}' here. Available stones: {available_names}")
    
    def handle_drop(self, item_name, player):
        item = self.get_item_from_inventory(item_name,player)
        if(item == None):
            print(f"You don't have the {item_name}.")
            return
        
        # remove the item from the inventory and put it in the object list
        player.inventory.remove(item)
        self.objects.append(item)
        print(f"You drop the {item.name}.")
        return 
    
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

    def handle_slide(self, target):
        words = [w for w in target.split() if w not in {"slot", "into", "to"}]
        if len(words) < 2:
            print("Specify an artifact and a slot number (1, 2, or 3). Example: 'slide gold 3'")
            return

        artifact_map = {
            "g": "[ gold ]", "gold": "[ gold ]",
            "m": "[ moss ]", "moss": "[ moss ]",
            "i": "[ iron ]", "iron": "[ iron ]",
        }
        artifact = artifact_map.get(words[0].lower().strip())
        slot_input = words[1]

        if not artifact:
            print("Invalid artifact. Choose 'gold', 'moss', or 'iron'.")
            return
        if slot_input not in ["1", "2", "3"]:
            print("Invalid slot. Choose slot 1, 2, or 3.")
            return

        idx = int(slot_input) - 1

        if artifact in self.trough:
            self.trough.remove(artifact)
        elif artifact in self.slots:
            self.slots[self.slots.index(artifact)] = self.empty

        displaced = self.slots[idx]
        if displaced != self.empty:
            self.trough.append(displaced)
            print(f"You slide the {displaced} artifact out of Slot {slot_input} and replace it with the {artifact} artifact.")
        else:
            print(f"You grind the {artifact} artifact into Slot {slot_input} with a heavy *CLUNK*.")

        self.slots[idx] = artifact

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
        artifact = self.slots[idx]
        if artifact == self.empty:
            print(f"Slot {slot_input} is already empty.")
            return
        self.slots[idx] = self.empty
        self.trough.append(artifact)
        print(f"You slide the {artifact} artifact out of Slot {slot_input} and back into the trough.")
        self.render_switchboard()

    def handle_look(self, target, player=None):
        if not target:
            self.describe_room()
            self.render_switchboard()
        elif target in ["switchboard", "board", "puzzle", "turntable"]:
            self.render_switchboard()
            print(
                "Faintly chiseled into the stone base is a warning:\n"
                "'ONE ARTIFACT ALIGNS ONE PATH. DO NOT PUT ANYTHING ELSE IN.'"
            )
        elif target in ["stones", "pile", "rocks", "floor", "ground"]:
            visible_stones = [obj.name for obj in self.objects if obj.visible]
            if visible_stones:
                print(f"Scattered near the tracks are small stones: {', '.join(visible_stones)}.")
            else:
                print("The pile of loose stones on the floor is empty.")
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
            print(
                "Heavy iron linkages run beneath the floorboards from the central switchboard to each cart's wheel-clamp.\n"
                "Down the tunnels, you can just make out rusted switch levers mounted beside the rails."
            )
        else:
            cleaned = target.replace("stone", "").replace("rock", "").strip()
            candidates = [obj for obj in self.objects if obj.visible]
            if player is not None:
                candidates.extend(item for item in player.inventory if isinstance(item, Object))
            match = next((obj for obj in candidates if obj.name.lower() == cleaned), None)
            if match:
                match.print_description()
                if match.state == "on_ground":
                    print(f"The {match.name} is on the ground.")
                else:
                    print(f"The {match.name} is in your inventory")
            else:
                print("Nothing to describe.")

    def describe_room(self):
        print(self.description)
        visible_objects = [obj.name for obj in self.objects if obj.visible]
        if visible_objects:
            print(f"Loose stones on the floor: {', '.join(visible_objects)}")
        print("Exits: " + ", ".join(self.exits))

    def get_player_stone(self, player):
        for item in player.inventory:
            if isinstance(item, ThrowingStone) or (
                isinstance(item, Object) and item.name in self.throwing_stone_names
            ):
                player.inventory.remove(item)
                item.state = "thrown"
                return item
        return None

    def prompt_hold_or_throw(self):
        """Prompts the player until they enter 'hold' or 'throw'."""
        while True:
            action = input("Do you 'hold' or 'throw'? > ").lower().strip()
            if action in ["hold", "h"]:
                return "hold"
            elif action in ["throw", "t"]:
                return "throw"
            print("Quick! Type 'hold' or 'throw'!")

    def ride_lever_sequence(self, player):
        """
        Correct sequence: 'hold' once, then 'throw' (requires a stone in inventory).
        Returns True if the player flips the lever, or False if they loop back.
        """
        print(
            "\nThe cart rattles forward and picks up speed! Ahead on the tunnel wall, "
            "you spot a rusted track-switch lever set to loop you back to the junction."
        )

        # Phase 1: Too far away — correct choice is 'hold'
        print("The lever is still a good distance down the track.")
        choice1 = self.prompt_hold_or_throw()

        if choice1 == "throw":
            stone = self.get_player_stone(player)
            if stone:
                print(
                    f"You hurl your {stone.name} too early! It bounces off the tunnel wall well short of the lever.\n"
                    "The track curves sharply, looping your cart all the way back to the junction!"
                )
            else:
                print(
                    "You reach into your pockets, but you don't have any stones to throw!\n"
                    "The track curves sharply, looping your cart all the way back to the junction!"
                )
            return False

        # Phase 2: Right alongside the lever — correct choice is 'throw'
        print("\nYou hold steady as the cart hurtles closer... The lever is nearly alongside you!")
        choice2 = self.prompt_hold_or_throw()

        if choice2 == "throw":
            stone = self.get_player_stone(player)
            if stone:
                print(
                    f"Direct hit! You whip your {stone.name} straight into the lever with a loud *CLANG*!\n"
                    "The rails snap over just in time, pulling you off the loop!"
                )
                player.score += 25
                return True
            else:
                print(
                    "You swing your arm—only to realize you have no stones to throw!\n"
                    "You roar past the lever and loop all the way back to the junction!"
                )
                return False
        else:
            print(
                "You hold too long! The lever blurs past behind you.\n"
                "The track curves sharply, looping your cart all the way back to the junction!"
            )
            return False

    def ride(self, target, player):
        unlocked = self.get_unlocked_cart()

        if not target.strip():
            if unlocked:
                normalized_cart = unlocked
            else:
                print("All four minecarts are locked to the tracks. Align the switchboard artifacts first.")
                return None
        else:
            words = target.split()
            if words and words[0] in ["cart", "minecart"]:
                words = words[1:]
            if words and words[-1] in ["cart", "minecart"]:
                words = words[:-1]
            choice = " ".join(words).strip()

            aliases = {
                "plain": "plain",
                "basic": "plain",
                "heavily damaged": "heavily damaged",
                "damaged": "heavily damaged",
                "gilded": "gilded",
                "gold": "gilded",
                "over-grown": "over-grown",
                "overgrown": "over-grown",
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

        if direction in ["south", "west"]:
            escaped_loop = self.ride_lever_sequence(player)
            if not escaped_loop:
                return None

        route_stories = {
            "north": (
                "The plain cart rattles past a row of old lanterns and magically climbs a steep slope. "
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