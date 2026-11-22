from unittest.mock import patch
from Room13_kiara import Room


class FakeItem:
    def __init__(self, name):
        self.name = name
        self.description = name
        self.can_be_gotten = True
        self.state = None


class FakePlayer:
    def __init__(self, items):
        self.inventory = []
        self.health = 100
        self.current_room = 1
        for item in items:
            self.inventory.append(FakeItem(item))

    def has_item(self, item_name):
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return True
        return False

    def show_inventory(self):
        print("Inventory:")

    def print_stats(self):
        print("Health:", self.health)


def test_enter_without_lamp_ends_game():
    room = Room()
    player = FakePlayer([])

    result = room.enter(player)

    assert result == "quit"
    assert player.health == 0
    assert player.current_room == 13


def test_enter_with_lamp_lights_cave():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", return_value="go south"):
        result = room.enter(player)

    assert result == "south"
    assert room.cave_is_lit is True


def test_east_requires_key():
    room = Room()

    assert room.move("east", FakePlayer(["lamp"])) is None
    assert room.move("east", FakePlayer(["lamp", "key"])) == "east"


def test_west_requires_hammer():
    room = Room()

    assert room.move("west", FakePlayer(["lamp"])) is None
    assert room.move("west", FakePlayer(["lamp", "hammer"])) == "west"


def test_south_always_open():
    room = Room()
    assert room.move("south", FakePlayer([])) == "south"


def test_down_riddle_correct_answer():
    room = Room()

    with patch("builtins.input", return_value="Fire"):
        assert room.move("down", FakePlayer([])) == "down"


def test_down_riddle_wrong_answer():
    room = Room()

    with patch("builtins.input", return_value="water"):
        assert room.move("down", FakePlayer([])) is None


def test_dragon_wakes_after_three_actions():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["look", "inventory", "hint"]):
        result = room.enter(player)

    assert result == "quit"
    assert player.health == 0
