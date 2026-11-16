from object import Object
from player import Player

class Pebble(Object):
    def __init__(self):
        super().__init__("pebble", "A small, round, and smooth pebble.", True, None, True)

    def use(self):
        print("You toss the pebble from one hand to another, then back. Looks fun.")

class Room:

    NARRATOR_LINES = [
        "A hole. Just a hole. You can't really see the bottom, but there probably is one. Best to ignore it and move on to another room.",
        "It's just a hole. Nothing has really changed about it, so why pay it more interest?",
        "Don't lean over the ledge like that, you might fall in.",
        "It's a hole, it can't be that interesting. Trust me, I'm trying to find a way to make it sound cooler, but it's just a hole.",
        "...",
        "..."
        "Last chance...",
        "Alright fine. WOWIE ZOWIE! You found the super secret bonus room easter egg where you jump in the hole, find out that it does in fact have a bottom and you break every bone in your body and die instantly. NICE!!!"
    ]

    def __init__(self):
        self.room_num = 14
        self.exists = ["south", "west", "up", "down"]
        self.objects = [Pebble()] #per-room list (not shared between rooms)
        self.hole_attempts = 0 #how many times have you tried to enter the hole?


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

        if verb in ["enter", "jump", "climb", "go", "move"] and "hole" in target:
            return self.try_hole(player)