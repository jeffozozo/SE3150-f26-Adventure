class Room:
    def __init__(self):
        self.room_num = 3
        self.description = "Room 3."
        self.exits = ['down']
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
                    return direction
            elif command == "look":
                if not target:
                    self.describe_room()
                else:
                    print("Nothing to describe.")
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
        print("Exits: " + ", ".join(self.exits))

    def move(self, direction):
        direction = {"w": "west", "u": "up", "d": "down"}.get(direction, direction)
        if direction in self.exits:
            return direction
        print("You can't go that way.")
        return None
