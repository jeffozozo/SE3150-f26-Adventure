#Make each minecart look different
#Make one go off
#Make some sort of junction puzzle that unlocks the minecarts.
#Maybe a sliding stones puzzle? Maybe use ascii art to show the stones position?

class Room:
    def __init__(self):
        self.room_num = 16
        self.description = (
            "You stand in an abandoned minecart junction. A battered minecart waits "
            "beside three tracks: north toward a lantern-lit tunnel, south into a "
            "deep cavern, and west through a narrow rock passage."
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
                direction = self.move(target)
                if direction is not None:
                    print("The path leads to a steep downward railway, which prevents you from walking that way. It does not seem that you can walk in any direction, but instead must ride one of the minecarts.")
            elif command in ["ride", "board"]:
                direction = self.ride(target)
                if direction is None:
                    print("Must provide a valid direction")
                if direction is not None:
                    return direction
            elif command == "look":
                if not target:
                    self.describe_room()
                elif target in ["cart", "minecart"]:
                    print(
                        "A battered minecart sits on the junction track. Its wheels "
                        "are rusty, but it looks sturdy enough to ride."
                    )
                elif target in ["track", "tracks", "junction"]:
                    print(
                        "The tracks branch north toward a lantern-lit tunnel, south "
                        "into a deep cavern, and west through a narrow rock passage."
                    )
                elif target in 
                else:
                    print("Nothing to describe.")
            elif command == "inventory":
                player.show_inventory()
            elif command == "stats":
                player.print_stats()
            elif command in ["help", "?"]:
                print(
                    "Commands: go, move, ride cart [direction], look, inventory, "
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
        direction = words[0] if words else ""
        direction = {"n": "north", "s": "south", "w": "west"}.get(
            direction, direction
        )

        if not direction:
            direction = input("Choose a track (north, south, or west): ").lower().strip()
            direction = {"n": "north", "s": "south", "w": "west"}.get(
                direction, direction
            )

        route_stories = {
            "north": (
                "The cart rattles past a row of old lanterns and climbs a steep "
                "slope. It bursts out of the tunnel toward the north."
            ),
            "south": (
                "The cart plunges into a cavern, skimming past glittering crystals "
                "before slowing at the southern passage."
            ),
            "west": (
                "The cart squeezes through a narrow rock passage as sparks fly from "
                "the rails. The track opens to the west."
            ),
        }
        if direction not in route_stories:
            print("Choose one of the minecart tracks: north, south, or west.")
            return None

        print(route_stories[direction])
        return direction
