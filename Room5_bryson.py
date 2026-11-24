from object import Object

CRASHED = "crashed"
BUTTON_REVEALED = "button_revealed"
TUNNEL_OPEN = "tunnel_open"

CRASH_SCREEN = """\
$ kubectl get pods -n ludwig-prod
NAME                       READY   STATUS             RESTARTS
dungeon-api-7f9c-x2k1      0/1     CrashLoopBackOff   4,812
torch-scheduler-55d-q9zz   0/1     CrashLoopBackOff   12,003
dragon-cache-0             0/1     CrashLoopBackOff   1,000,000+
moat-ingress-6b4-lp0w      0/1     Pending            ...since 1347"""

FIXED_SCREEN = """\
$ kubectl get pods -n ludwig-prod
NAME                       READY   STATUS    RESTARTS
dungeon-api-7f9c-x2k1      1/1     Running   0
torch-scheduler-55d-q9zz   1/1     Running   0
dragon-cache-0             1/1     Running   0
moat-ingress-6b4-lp0w      1/1     Running   0
All pods Running. Somehow."""


class Bat(Object):
    def use(self):
        print("You take a practice swing. Whoosh.")


class Laptop(Object):
    def use(self):
        if self.state == "dented":
            print(FIXED_SCREEN)
        else:
            print(CRASH_SCREEN)


class Button(Object):
    def use(self):
        if self.state == "pressed":
            print("You press the button again. The tunnel is already open.")
        else:
            self.state = "pressed"
            print("CLICK. Somewhere behind the east wall, gears start grinding.")


class Room:
    def __init__(self):
        self.room_num = 5
        self.puzzle_state = CRASHED

        self.bat = Bat("bat", "A sturdy wooden bat. Someone wrote 'PROD FIX' on it in marker.",
                       True, "intact", False)
        self.laptop = Laptop("laptop", "A cracked laptop bolted to the rack. The screen reads: "
                             "'deployment/ludwig-prod: 0/47 pods ready'. Maybe try using it.",
                             False, "crashlooping", True)
        self.button = Button("button", "A big red button. It practically begs to be used.",
                             False, "unpressed", False)
        self.objects = [self.bat, self.laptop, self.button]

    def enter(self, player):
        if player.current_room == 16 and self.puzzle_state != TUNNEL_OPEN:
            self.reveal_button()
            self.unlock_tunnel()
            print("Your minecart rockets out of the tunnel and rams the server rack.\n"
                  "WHACK! An old keyboard flies off the junk pile and hits the laptop. The screen flickers\n"
                  "green, and a big red button on the rack clicks in. The wall stays open behind you.")
        player.current_room = self.room_num
        self.describe_room()
        while True:
            direction = self.handle_command(input("> "), player)
            if direction is not None:
                return direction

    def handle_command(self, command, player):
        parts = command.lower().split(maxsplit=1)
        if not parts:
            print("Type 'help' for a list of commands.")
            return None

        verb = parts[0]
        target = parts[1].strip() if len(parts) > 1 else ""

        if verb in ["go", "move"]:
            return self.move(target)
        elif verb == "quit":
            return self.quit_game(player)
        elif verb == "look":
            self.look(target, player)
        elif verb in ["get", "take"]:
            self.get(target, player)
        elif verb == "drop":
            self.drop(target, player)
        elif verb == "use":
            self.use(target, player)
        elif verb == "hit":
            self.hit(target, player)
        elif verb == "inventory":
            player.show_inventory()
        elif verb == "stats":
            player.print_stats()
        elif verb in ["help", "?"]:
            self.show_help()
        elif verb == "hint":
            self.show_hint()
        else:
            print("You can't do that here. Type 'help' for commands or 'hint' for a clue.")
        return None

    def describe_room(self):
        print("You are in a torch-lit stone room. A server rack hums in the corner, a laptop\n"
              "bolted to its side. A pile of 'decommissioned' hardware is heaped behind the rack.\n"
              "A heavy iron door leads west, and a rusty ladder climbs up through a grate.")
        if self.puzzle_state == CRASHED:
            print("The laptop screen glows an angry red.")
        elif self.puzzle_state == BUTTON_REVEALED:
            print("The laptop is dented, and a panel has popped off the rack, exposing a big red button.")
        else:
            print("The east wall has slid aside, revealing a mining tunnel leading east.\n"
                  "A minecart waits on the tracks.")

        for item in self.objects:
            if item.visible:
                print(f"There is a {item.name} here.")

    def available_exits(self):
        if self.puzzle_state == TUNNEL_OPEN:
            return ["west", "up", "east"]
        return ["west", "up"]

    def move(self, direction):
        direction = {"w": "west", "u": "up", "e": "east"}.get(direction, direction)
        if direction in self.available_exits():
            if direction == "east":
                print("You leap into the minecart. It plunges into the dark, screeching around every bend!")
            else:
                print(f"You head {direction}.")
            return direction
        if direction == "east":
            print("There's just a stone wall that way.")
        else:
            print("You can't go that way.")
        return None

    def find_in_room(self, name):
        for item in self.objects:
            if item.visible and item.name.lower() == name:
                return item
        return None

    def look(self, target, player):
        if not target:
            self.describe_room()
            return
        if target == "rack":
            self.look_rack()
            return

        item = player.get_item(target) or self.find_in_room(target)
        if item is None:
            print(f"You don't see a {target} here.")
            return
        print(item.description)
        if item.state is not None:
            print(f"The {item.name} is {item.state}.")

    def look_rack(self):
        print("The rack blinks and whirs. Behind it is a pile of old hardware.")
        if not self.bat.visible:
            self.bat.visible = True
            print("Wedged in the pile, you spot a bat.")

    def get(self, name, player):
        if not name:
            print("Get what?")
            return
        if player.has_item(name):
            print(f"You already have the {name}.")
            return

        item = self.find_in_room(name)
        if item is None:
            print(f"There is no {name} here.")
        elif not item.can_be_gotten:
            print(f"You can't take the {item.name}.")
        else:
            self.objects.remove(item)
            player.inventory.append(item)
            print(f"You take the {item.name}.")

    def drop(self, name, player):
        if not name:
            print("Drop what?")
            return
        item = player.get_item(name)
        if item is None:
            print(f"You don't have a {name}.")
            return
        player.inventory.remove(item)
        item.visible = True
        self.objects.append(item)
        print(f"You drop the {item.name}.")

    def use(self, name, player):
        if not name:
            print("Use what?")
            return

        item = player.get_item(name) or self.find_in_room(name)
        if item is None:
            print(f"You don't have a {name} to use.")
            return
        if name == "bat":
            if player.has_item("bat"):
                self.hit_laptop(player)
            else:
                print("You need to be holding the bat.")
            return

        item.use()
        if item is self.button:
            self.open_tunnel(player)

    def hit(self, target, player):
        if not target:
            print("Hit what?")
        elif "laptop" not in target:
            print("Hitting that won't help.")
        elif not player.has_item("bat"):
            print("You slap the laptop. It does not care.")
        else:
            self.hit_laptop(player)

    def hit_laptop(self, player):
        if self.puzzle_state != CRASHED:
            print("It's already dented.")
            return
        self.reveal_button()
        player.score += 10
        print("WHACK! The laptop screen flickers green. A panel pops off the rack, revealing a big red button.")

    def open_tunnel(self, player):
        if self.puzzle_state != BUTTON_REVEALED:
            return
        self.unlock_tunnel()
        player.score += 25
        print("The east wall slides aside, revealing a mining tunnel leading east.")

    def reveal_button(self):
        self.puzzle_state = BUTTON_REVEALED
        self.laptop.state = "dented"
        self.laptop.description = ("A dented laptop bolted to the rack. The screen flickers: "
                                   "'deployment/ludwig-prod: 47/47 pods ready'. Nobody knows why.")
        self.button.visible = True

    def unlock_tunnel(self):
        self.puzzle_state = TUNNEL_OPEN
        self.button.state = "pressed"

    def show_help(self):
        print("Commands: go/move <direction>, look [item], get/take <item>, drop <item>, use <item>,")
        print("          hit <item>, inventory, stats, help/?, hint, quit")
        print("Exits: " + ", ".join(self.available_exits()))

    def show_hint(self):
        if self.puzzle_state == CRASHED and not self.bat.visible:
            print("That rack looks like it's hiding something.")
        elif self.puzzle_state == CRASHED:
            print("Have you tried turning it off and on again... harder?")
        elif self.puzzle_state == BUTTON_REVEALED:
            print("Big red buttons exist to be used.")
        else:
            print("The tunnel east is open.")

    def quit_game(self, player):
        if input("Are you sure? (y/n) ").lower().strip().startswith("y"):
            player.print_stats()
            return "quit"
        return None
