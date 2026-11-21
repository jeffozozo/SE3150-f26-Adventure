#Make each minecart look different
#Make one go off
#Make some sort of junction puzzle that unlocks the minecarts.
#Maybe a sliding stones puzzle? Maybe use ascii art to show the stones position?

class Room:
    def __init__(self):
        self.room_num = 16
        self.description = (
            '''You stand in an abandoned minecart junction. Four battered minecarts wait, each on a seperate 
            tracks: north toward a briefly lantern-lit tunnel that quickly fades into crushing darkness, south into a 
            deep cavern, east seems to be blocked behind a rockfall, and west through a narrow rock passage.
            There are four minecarts, one for each track. You see a gilded cart, an over-grown cart, a plain cart, and a heavily damaged cart'''
        )
        self.exits = ['north', 'west', 'south']
        self.objects = []

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
                print("The path eventually leads to a steep downward railway, which prevents you from walking that way. It does not seem that you can walk in any direction, but instead must ride one of the minecarts.")
            elif command in ["ride", "board"]:
                cart = self.ride(target)
                if cart is None:
                    print("Must choose a valid cart (gilded cart, plain cart, heavily damaged cart, over-grown cart)")
                else:
                    return cart
            elif command == "look":
                if not target:
                    self.describe_room()
                elif target in ["gilded cart", "gold cart", "gilded minecart", "gold minecart"]:
                    print(
                        "You see a pristine, gold covered minecart that looks like it has hardly been used. The tracks under it look equally well-maintained."
                    )
                elif target in ["plain cart", "basic cart", "plain minecart", "basic minecart"]:
                    print(
                        "You see a dirty and well-used minecart sits on the junction track. Its wheels "
                        "are rusty, but it looks sturdy enough to ride."
                    )
                elif target == "heavily damaged cart":
                    print(
                        "You see a heavily dented and battered minecart that looks like it has been dropped from a great height."
                        "It's track looks old but barely used."
                    )
                elif target in ["over-grown cart", "overgrown cart", "overgrown minecart", "over-grown minecart"]:
                    print(
                        "You see a cart over-grown with so many weeds that looks as though it was recently retrieved from a jungle after being abandoned for 70 years." 
                        "The tracks it sits on look newly made, though it might be difficult to get in to the cart."
                    )
                elif target in ["track", "tracks", "junction"]:
                    print(
                        "The tracks branch north toward a lantern-lit tunnel, south "
                        "into a deep cavern, and west through a narrow rock passage."
                    )
                else:
                    print("Nothing to describe.")
            elif command == "inventory":
                player.show_inventory()
            elif command == "stats":
                player.print_stats()
            elif command in ["help", "?"]:
                print(
                    "Commands: go, move, ride [cart name], look, inventory, "
                    "stats, help, hint, quit"
                )
                print("Exits: " + ", ".join(self.exits))
            elif command == "hint":
                print("Board the minecart and choose north, south, or west.")
            elif command == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
            else:
                print("Command unavailable.")

    def describe_room(self):
        print(self.description)
        print("Exits: " + ", ".join(self.exits))

    def move(self, direction):
        direction = {"w": "west", "u": "up", "d": "down"}.get(direction, direction)
        if direction in self.exits:
            return direction
        print("You can't go that way.")
        return None

    def ride(self, target):
        words = target.split()
        if words and words[0] in ["cart", "minecart"]:
            words = words[1:]
        choice = " ".join(words).strip()

        cart_routes = {
            "gilded cart": "north",
            "gold cart": "north",
            "gilded minecart": "north",
            "gold minecart": "north",
            "gilded": "north",
            "plain cart": "south",
            "basic cart": "south",
            "plain minecart": "south",
            "basic minecart": "south",
            "plain": "south",
            "heavily damaged cart": "west",
            "heavily damaged minecart": "west",
            "damaged cart": "west",
            "damaged": "west",
            "over-grown cart": "east",
            "overgrown cart": "east",
            "over-grown minecart": "east",
            "overgrown minecart": "east",
            "overgrown": "east",
        }
        direction = cart_routes.get(choice)

        if choice in ["n", "north", "s", "south", "e", "east", "w", "west"]:
            direction = {
                "n": "north",
                "s": "south",
                "e": "east",
                "w": "west",
            }.get(choice, choice)

        if not choice:
            direction = input(
                "Choose a cart (gilded, plain, heavily damaged, or over-grown): "
            ).lower().strip()
            choice = direction
            direction = cart_routes.get(choice)
            if choice in ["n", "north", "s", "south", "e", "east", "w", "west"]:
                direction = {
                    "n": "north",
                    "s": "south",
                    "e": "east",
                    "w": "west",
                }.get(choice, choice)

        route_stories = {
            "north": (
                "The cart rattles past a row of old lanterns and climbs a steep "
                "slope. It bursts out of the tunnel toward the north."
            ),
            "south": (
                "The cart plunges into a cavern, skimming past glittering crystals "
                "before slowing at the southern passage."
            ),
            "east": (
                "The cart reaches a rockfall blocking the eastern track. "
                "You cannot continue this way."
            ),
            "west": (
                "The cart squeezes through a narrow rock passage as sparks fly from "
                "the rails. The track opens to the west."
            ),
        }
        if direction not in route_stories:
            print(
                "Choose one of the minecarts: gilded cart, plain cart, "
                "heavily damaged cart, or over-grown cart."
            )
            return None

        print(route_stories[direction])
        return direction
