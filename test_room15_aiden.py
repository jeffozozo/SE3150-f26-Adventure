
import pytest

from Room15_aiden import Room, Gem


# Mock Player

class DummyPlayer:

    def __init__(self):
        self.score = 0
        self.inventory = []
        self.current_room = None

    def has_item(self, item_name):
        return any(
            item.name.lower() == item_name.lower()
            for item in self.inventory
        )

    def show_inventory(self):
        print("Inventory displayed.")

    def print_stats(self):
        print(f"Score: {self.score}")


# Test fixtures

@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return DummyPlayer()


@pytest.fixture
def gem():
    return Gem(
        "Gem",
        "A mysterious glowing gem.",
        True,
        "glowing",
        True
    )


# 1-3: Room initialization

def test_room_number(room):
    assert room.room_num == 15


def test_room_exits(room):
    assert room.exits == ["east", "down"]


def test_initial_lights(room):
    assert room.lights == [
        True, False, True,
        False, True, False,
        True, False, True
    ]


# 4-5: Checking puzzle state

def test_all_on_false(room):
    assert room.all_on() is False


def test_all_on_true(room):
    room.lights = [True] * 9
    assert room.all_on() is True


# 6-11: Pressing lights

def test_press_turns_light_on(room):
    room.press(2)
    assert room.lights[1] is True


def test_press_turns_light_off(room):
    room.press(1)
    assert room.lights[0] is False


def test_press_twice_restores_light(room):
    original = room.lights.copy()

    room.press(2)
    room.press(2)

    assert room.lights == original


def test_press_zero_is_invalid(room):
    original = room.lights.copy()

    room.press(0)

    assert room.lights == original


def test_press_ten_is_invalid(room):
    original = room.lights.copy()

    room.press(10)

    assert room.lights == original


def test_press_non_integer_is_invalid(room):
    original = room.lights.copy()

    room.press("five")

    assert room.lights == original


# 12-13: Puzzle completion

def test_solution_solves_room(room):
    for n in [2, 4, 6, 8]:
        room.press(n)

    assert room.all_on() is True
    assert room.solved is True


def test_cannot_change_lights_after_solving(room):
    room.lights = [True] * 9
    room.solved = True

    original = room.lights.copy()

    room.press(1)

    assert room.lights == original


# 14-17: Movement

def test_cannot_move_before_solving(room):
    assert room.move("east") is None


def test_move_east_after_solving(room):
    room.solved = True

    assert room.move("east") == "east"


def test_move_down_after_solving(room):
    room.solved = True

    assert room.move("down") == "down"


def test_invalid_direction(room):
    room.solved = True

    assert room.move("north") is None


# 18-20: Gem functionality

def test_gem_initial_state(gem):
    assert gem.state == "glowing"


def test_gem_increases_player_score(gem, player):
    gem.use(player)

    assert player.score == 10
    assert gem.state == "dull"


def test_gem_only_rewards_once(gem, player):
    gem.use(player)
    gem.use(player)

    assert player.score == 10
    assert gem.state == "dull"


# 21-25: Getting objects

def test_get_adds_item_to_inventory(room, player, gem):
    room.objects.append(gem)

    room.get("Gem", player)

    assert gem in player.inventory


def test_get_removes_item_from_room(room, player, gem):
    room.objects.append(gem)

    room.get("Gem", player)

    assert gem not in room.objects


def test_cannot_get_unobtainable_item(room, player):
    item = Gem("Statue", "A large statue.", False, None, True)
    room.objects.append(item)

    room.get("Statue", player)

    assert item not in player.inventory
    assert item in room.objects


def test_get_nonexistent_item(room, player):
    room.get("Sword", player)

    assert len(player.inventory) == 0


def test_cannot_get_duplicate_item(room, player, gem):
    player.inventory.append(gem)
    room.objects.append(gem)

    room.get("Gem", player)

    assert player.inventory.count(gem) == 1


# 26-27: Dropping objects

def test_drop_adds_item_to_room(room, player, gem):
    player.inventory.append(gem)

    room.drop("Gem", player)

    assert gem in room.objects


def test_drop_removes_item_from_inventory(room, player, gem):
    player.inventory.append(gem)

    room.drop("Gem", player)

    assert gem not in player.inventory


# 28: Looking at objects

def test_look_at_item(room, player, gem, capsys):
    room.objects.append(gem)

    room.look("gem", player)

    output = capsys.readouterr().out

    assert "mysterious glowing gem" in output


# 29: Using nonexistent objects

def test_use_nonexistent_item(room, player, capsys):
    room.use("Sword", player)

    output = capsys.readouterr().out

    assert "can't use that" in output


# 30: Quitting

def test_quit_game_confirmed(player, monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")

    room = Room()

    result = room.quit_game(player)

    assert result == "quit"
