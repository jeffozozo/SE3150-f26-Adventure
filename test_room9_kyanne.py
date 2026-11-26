import pytest

from player import Player
from Room9_kyanne import Room, Sandwich


# ----- Helpers -----

# Runs the room's enter() as if the player typed each command in the list.
# Returns whatever enter() returns.
def play(room, player, commands, monkeypatch):
    typed = iter(commands)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(typed))
    return room.enter(player)


# Everything needed to solve the room, in order.
SOLVE = [
    "open fridge",
    "take bread", "take cheese", "take tomato", "take jar",
    "open jar",
    "stack bread", "stack cheese", "stack tomato",
    "stack pickles", "stack cheese", "stack bread",
    "serve sandwich",
]

# A sandwich in the wrong order (bread on the bottom, then pickles).
WRONG = ["stack bread", "stack pickles", "serve"]

# Ends a test that should leave the player in the room.
QUIT = ["quit", "y"]


@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return Player("Tester", 100, "healthy", 0)


# ----- Entering the room -----

def test_enter_sets_current_room_to_9(room, player, monkeypatch):
    play(room, player, QUIT, monkeypatch)
    assert player.current_room == 9


# ----- Exits -----

def test_go_north_is_always_open(room, player, monkeypatch):
    assert play(room, player, ["go north"], monkeypatch) == "north"


def test_go_up_is_blocked_before_solving(room, player, monkeypatch, capsys):
    result = play(room, player, ["go up"] + QUIT, monkeypatch)
    assert result == "quit"
    assert "Chef Gustav floats in your way." in capsys.readouterr().out


def test_go_down_is_blocked_before_solving(room, player, monkeypatch, capsys):
    result = play(room, player, ["go down"] + QUIT, monkeypatch)
    assert result == "quit"
    assert "Chef Gustav floats in your way." in capsys.readouterr().out


def test_other_directions_are_not_exits(room, player, monkeypatch, capsys):
    result = play(room, player, ["go west"] + QUIT, monkeypatch)
    assert result == "quit"
    assert "You can't go that way." in capsys.readouterr().out


# ----- The fridge and the jar -----

def test_cannot_take_fridge_items_before_opening_it(room, player, monkeypatch):
    play(room, player, ["take cheese", "take tomato", "take jar"] + QUIT, monkeypatch)
    assert player.inventory == []


def test_opening_the_fridge_lets_you_take_the_items(room, player, monkeypatch):
    play(room, player, ["open fridge", "take cheese", "take tomato", "take jar"] + QUIT, monkeypatch)
    assert room.cheese in player.inventory
    assert room.tomato in player.inventory
    assert room.jar in player.inventory


def test_pickles_cannot_be_stacked_before_the_jar_is_open(room, player, monkeypatch):
    play(room, player, ["open fridge", "take jar", "stack pickles"] + QUIT, monkeypatch)
    assert room.plate.stack == []


def test_pickles_can_be_stacked_after_the_jar_is_open(room, player, monkeypatch):
    play(room, player, ["open fridge", "take jar", "open jar", "stack pickles"] + QUIT, monkeypatch)
    assert room.plate.stack == ["pickles"]


# ----- Stacking -----

def test_cannot_stack_an_item_not_in_inventory(room, player, monkeypatch):
    play(room, player, ["stack bread"] + QUIT, monkeypatch)
    assert room.plate.stack == []


def test_stacking_keeps_the_item_in_inventory(room, player, monkeypatch):
    play(room, player, ["take bread", "stack bread", "stack bread"] + QUIT, monkeypatch)
    assert room.plate.stack == ["bread", "bread"]
    assert room.bread in player.inventory


# ----- Serving -----

def test_correct_sandwich_solves_the_room(room, player, monkeypatch):
    play(room, player, SOLVE + QUIT, monkeypatch)
    assert room.solved == True
    assert player.score == 25
    assert player.has_item("Sandwich")


def test_up_opens_after_solving(room, player, monkeypatch):
    assert play(room, player, SOLVE + ["go up"], monkeypatch) == "up"


def test_down_opens_after_solving(room, player, monkeypatch):
    assert play(room, player, SOLVE + ["go down"], monkeypatch) == "down"


def test_wrong_sandwich_adds_anger_and_clears_the_plate(room, player, monkeypatch):
    play(room, player, ["open fridge", "take bread", "take jar", "open jar"] + WRONG + QUIT, monkeypatch)
    assert room.anger == 1
    assert room.plate.stack == []
    assert room.solved == False


def test_third_wrong_sandwich_throws_the_pan(room, player, monkeypatch, capsys):
    setup = ["open fridge", "take bread", "take jar", "open jar"]
    play(room, player, setup + WRONG + WRONG + WRONG + QUIT, monkeypatch)
    assert player.health == 95
    assert room.anger == 0
    assert "CLANG!" in capsys.readouterr().out


def test_serving_an_empty_plate_is_not_a_mistake(room, player, monkeypatch):
    play(room, player, ["serve"] + QUIT, monkeypatch)
    assert room.anger == 0
    assert player.health == 100


def test_serving_again_after_solving_gives_no_more_points(room, player, monkeypatch):
    again = ["stack bread", "stack cheese", "stack tomato",
             "stack pickles", "stack cheese", "stack bread", "serve"]
    play(room, player, SOLVE + again + QUIT, monkeypatch)
    assert player.score == 25


# ----- The sandwich -----

def test_eating_the_sandwich_heals_25_and_removes_it(room, player, monkeypatch):
    play(room, player, SOLVE + ["eat sandwich"] + QUIT, monkeypatch)
    assert player.health == 125
    assert not player.has_item("Sandwich")


def test_sandwich_heals_when_used_outside_the_room(player):
    sandwich = Sandwich("Sandwich", "A sandwich.", True, None, True, player)
    player.inventory.append(sandwich)
    sandwich.use()
    assert player.health == 125
    assert sandwich not in player.inventory


# ----- Coming back later -----

def test_exits_stay_open_when_reentering_after_solving(room, player, monkeypatch):
    play(room, player, SOLVE + ["go north"], monkeypatch)
    assert play(room, player, ["go up"], monkeypatch) == "up"


# ----- Get and drop -----

def test_get_and_drop_move_items(room, player, monkeypatch):
    play(room, player, ["take bread"] + QUIT, monkeypatch)
    assert room.bread in player.inventory
    assert room.bread not in room.objects

    play(room, player, ["drop bread"] + QUIT, monkeypatch)
    assert room.bread not in player.inventory
    assert room.bread in room.objects


def test_fridge_note_and_plate_cannot_be_taken(room, player, monkeypatch):
    play(room, player, ["take fridge", "take recipe", "take plate"] + QUIT, monkeypatch)
    assert player.inventory == []


# ----- Quit -----

def test_quit_yes_returns_quit(room, player, monkeypatch):
    assert play(room, player, ["quit", "y"], monkeypatch) == "quit"


def test_quit_no_stays_in_the_room(room, player, monkeypatch):
    assert play(room, player, ["quit", "n", "go north"], monkeypatch) == "north"
