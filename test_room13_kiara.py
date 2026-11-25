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
        return any(item.name.lower() == item_name.lower() for item in self.inventory)

    def show_inventory(self):
        print("Inventory:")

    def print_stats(self):
        print("Health:", self.health)


def test_enter_without_lamp_dies_and_returns_valid_exit():
    room = Room()
    player = FakePlayer([])

    result = room.enter(player)

    assert result == "south"
    assert player.health == 0
    assert player.current_room == 13


def test_cave_lights_only_after_using_lamp():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["use lamp", "go south"]):
        result = room.enter(player)

    assert result == "south"
    assert room.cave_is_lit is True
    assert player.inventory[0].state == "on"
    assert [item.name.lower() for item in room.objects] == ["key", "hammer"]


def test_east_requires_key_after_cave_is_lit():
    room = Room()
    room.cave_is_lit = True

    assert room.move("east", FakePlayer(["lamp"])) is None
    assert room.move("east", FakePlayer(["lamp", "key"])) == "east"


def test_west_requires_hammer_after_cave_is_lit():
    room = Room()
    room.cave_is_lit = True

    assert room.move("west", FakePlayer(["lamp"])) is None
    assert room.move("west", FakePlayer(["lamp", "hammer"])) == "west"


def test_south_always_open():
    room = Room()
    assert room.move("south", FakePlayer([])) == "south"


def test_down_requires_finding_trapdoor_and_correct_answer():
    room = Room()
    player = FakePlayer([])
    room.cave_is_lit = True

    assert room.move("down", player) is None
    room.trapdoor_found = True
    with patch("builtins.input", return_value="Fire"):
        assert room.move("down", player) == "down"


def test_down_riddle_rejects_wrong_answer():
    room = Room()
    room.cave_is_lit = True
    room.trapdoor_found = True

    with patch("builtins.input", return_value="water"):
        assert room.move("down", FakePlayer([])) is None


def test_look_can_inspect_inventory_item(capsys):
    room = Room()
    player = FakePlayer(["key"])

    room.look("key", player)

    assert "key" in capsys.readouterr().out


def test_look_can_inspect_room_item_after_lighting(capsys):
    room = Room()
    room.cave_is_lit = True

    room.look("hammer", FakePlayer([]))

    assert "western stone barrier" in capsys.readouterr().out


def test_player_can_take_only_one_route_item():
    room = Room()
    room.cave_is_lit = True
    player = FakePlayer(["lamp"])

    assert room.get("key", player) is True
    assert room.get("hammer", player) is False
    assert room.drop("key", player) is True
    assert room.get("hammer", player) is True


def test_search_reveals_trapdoor_after_lighting_cave():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["use lamp", "search", "go down", "fire"]):
        result = room.enter(player)

    assert result == "down"
    assert room.trapdoor_found is True


def test_help_hint_inventory_stats_and_blocked_exit_do_not_use_actions():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch(
        "builtins.input",
        side_effect=["help", "hint", "inventory", "stats", "go east", "use lamp", "go south"],
    ):
        result = room.enter(player)

    assert result == "south"
    assert room.actions_taken == 1


def test_dragon_wakes_after_four_actions_and_returns_valid_exit():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["use lamp", "get key", "look key", "look key"]):
        result = room.enter(player)

    assert result == "south"
    assert player.health == 0


def test_invalid_direction_does_not_use_action():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["go north", "go south"]):
        result = room.enter(player)

    assert result == "south"
    assert room.actions_taken == 0


def test_declining_quit_continues_and_confirming_quit_returns_quit():
    room = Room()
    player = FakePlayer(["lamp"])

    with patch("builtins.input", side_effect=["quit", "n", "go south"]):
        assert room.enter(player) == "south"

    room = Room()
    player = FakePlayer(["lamp"])
    with patch("builtins.input", side_effect=["quit", "y"]):
        assert room.enter(player) == "quit"
