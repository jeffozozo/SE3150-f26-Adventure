import pytest

from player import Player
from object import Object
from Room11_AustinR import Room, Rope

class FakeLamp(Object):
    def __init__(self):
        super().__init__("lamp", "A lamp that can be turned on and off.", True, "off", True)

    def use(self):
        self.state = "on" if self.state == "off" else "off"
        if self.state == "on":
            print("You turn on the lamp.")
        else:
            print("You turn off the lamp.")

@pytest.fixture

def room():
    return Room()

@pytest.fixture

def player():
    return Player(name="Test Player", current_room=0, health=100, condition="healthy", inventory=[])

def play(monkeypatch, room, player, commands):
    """Feed the commands to the room as if a user typed them, and return what enter() returns."""
    typed = iter(commands)

    def fake_input(prompt=""):
        try:
            return next(typed)
        except StopIteration:
            raise AssertionError("The room asked for more input than the test supplied")

    monkeypatch.setattr("builtins.input", fake_input)
    return room.enter(player)