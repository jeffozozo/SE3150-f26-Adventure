class Room:
    def __init__(self):
        self.room_num = 13
        self.description = (
            "Room 13 is a dark, cool cave. A dragon sleeps nearby, its "
            "heavy breathing echoing off the walls."
        )
        self.exits = ["south", "east", "west", "down"]
        self.actions_before_dragon_wakes = 3
        self.actions_taken = 0
        self.cave_is_lit = False
        self.down_puzzle_solved = False
        self.west_crawl_started = False

    def enter(self, player):
        player.current_room = self.room_num
        self.actions_taken = 0
        self.down_puzzle_solved = False
        self.west_crawl_started = False

        if not (player.has_item("lighter") or player.has_item("lamp")):
            print("You have no lighter to see or escape. The dragon wakes and eats you!")
            player.health = 0
            player.print_stats()
            return "quit"

        self.describe_room()
        print(
            "The dragon is waking. Leave quickly! East needs both a key and a gem; "
            "down requires solving a riddle; west is an unstable crawl; south leads onward."
        )

        while True:
            parts = input("> ").lower().split(maxsplit=1)
            if not parts:
                continue

            command = parts[0]
            target = parts[1].strip() if len(parts) > 1 else ""

            if command in ["go", "move"]:
                direction = self._normalize_direction(target)
                if direction not in self.exits:
                    print("You can't go that way.")
                elif direction == "east":
                    if not (player.has_item("key") and player.has_item("gem")):
                        print("The east door needs both a key and a gem. The dragon stirs!")
                    else:
                        print("The key and gem unlock the east door. You escape the cave!")
                        return "east"
                elif direction == "down":
                    if not self.down_puzzle_solved:
                        print("A stone hatch blocks the way down. Type 'answer <riddle answer>'.")
                    else:
                        print("The hatch opens and you hurry down before the dragon wakes.")
                        return "down"
                elif direction == "west":
                    if not self.west_crawl_started:
                        self.west_crawl_started = True
                        print("Loose rocks block the west passage. Type 'crawl west' to squeeze through.")
                    else:
                        print("You crawl through the unstable rocks and escape west!")
                        return "west"
                else:
                    print("You hurry south into the next room, leaving the dragon behind.")
                    return "south"
            elif command == "crawl":
                if target not in ["", "west", "rocks"] or not self.west_crawl_started:
                    print("There is no crawlway to use. Try 'go west' first.")
                else:
                    print("You squeeze through the shifting rocks and escape west!")
                    return "west"
            elif command == "answer":
                if target == "shadow":
                    self.down_puzzle_solved = True
                    print("Correct! The stone hatch unlocks. Go down now!")
                else:
                    print("That answer is wrong. The hatch stays shut.")
            elif command == "look":
                if target in ["", "cave", "room"]:
                    self.describe_room()
                elif target == "dragon":
                    print("The dragon is asleep, but it will not stay that way for long.")
                elif target in ["lighter", "lamp"]:
                    print("Your light can help you see the cave, but it won't stop the dragon.")
                elif target == "hatch":
                    print("A stone hatch blocks the way down. A riddle is carved into it.")
                    print("I follow you everywhere, but disappear in the dark. What am I?")
                elif target in ["rocks", "west"]:
                    print("Loose rocks have nearly sealed the west passage.")
                else:
                    print("You can't see anything else in the darkness.")
            elif command == "use":
                if target in ["lighter", "lamp"] and (
                    player.has_item("lighter") or player.has_item("lamp")
                ):
                    self.cave_is_lit = True
                    print("You light your lighter. The cave exits and the stone hatch are visible.")
                else:
                    print("You can only use the lighter or lamp you brought with you.")
            elif command == "inventory":
                player.show_inventory()
            elif command == "stats":
                player.print_stats()
            elif command in ["help", "?"]:
                print(
                    "Commands: go <direction>, use lighter, look, answer <answer>, "
                    "crawl west, inventory, stats, hint, quit"
                )
                print("Exits: " + ", ".join(self.exits))
            elif command == "hint":
                print("The hatch answer is something that follows you in the light.")
                print("For west, go west and then crawl. For south, just go south.")
            elif command == "quit":
                if input("Are you sure? (y/n) ").lower().startswith("y"):
                    player.print_stats()
                    return "quit"
                continue
            else:
                print("Command unavailable. Type 'help' or 'hint' for guidance.")

            self.actions_taken += 1
            actions_left = self.actions_before_dragon_wakes - self.actions_taken
            if actions_left > 0:
                print(f"The dragon stirs. {actions_left} action(s) left!")
            else:
                print("The dragon wakes, catches you in the cave, and eats you!")
                player.health = 0
                player.print_stats()
                return "quit"

    def describe_room(self):
        print(self.description)
        if self.cave_is_lit:
            print("Your lighter reveals the cave exits: " + ", ".join(self.exits))
        else:
            print("It is too dark to see the exits. You hear a dragon sleeping nearby.")

    def _normalize_direction(self, direction):
        return {
            "s": "south",
            "e": "east",
            "w": "west",
            "d": "down",
        }.get(direction, direction)
