import builtins

import pytest

from player import Player
from Room14_austin_sundloff import Room


@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return Player(name="Tester", health=100, condition="healthy", current_room=0)


def feed_input(monkeypatch, commands):
    """Fake user: each input() call returns the next command."""
    answers = iter(commands)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(answers))


# ---------------- the hole ----------------

def test_first_six_attempts_are_refused(room, player):
    for _ in range(6):
        assert room.process_command("enter hole", player) is None
    assert player.is_alive()


def test_each_refusal_is_a_different_line(room, player, capsys):
    lines = []
    for _ in range(6):
        room.process_command("enter hole", player)
        lines.append(capsys.readouterr().out)
    assert len(set(lines)) == 6


def test_seventh_attempt_kills_player(room, player):
    for _ in range(6):
        room.process_command("enter hole", player)
    result = room.process_command("enter hole", player)
    assert result == "down"          # a valid exit, so Adventure.py accepts it
    assert result in room.exits
    assert not player.is_alive()
    assert "stuck in a hole" in player.condition


@pytest.mark.parametrize("command", ["enter hole", "jump in hole", "jump into the hole",
                                     "go hole", "climb into hole", "move hole"])
def test_different_ways_to_try_the_hole(room, player, command):
    room.process_command(command, player)
    assert room.hole_attempts == 1


def test_whole_hole_scenario_through_enter(room, player, monkeypatch):
    feed_input(monkeypatch, ["enter hole"] * 7)
    assert room.enter(player) == "down"
    assert player.health == 0


# ---------------- exits ----------------

@pytest.mark.parametrize("command, expected", [
    ("go south", "south"), ("go west", "west"), ("go up", "up"), ("go down", "down"),
    ("move s", "south"), ("go w", "west"), ("go u", "up"), ("go d", "down"),
])
def test_valid_exits(room, player, command, expected):
    assert room.process_command(command, player) == expected
    assert player.is_alive()


@pytest.mark.parametrize("command", ["go north", "go east", "go"])
def test_invalid_exits(room, player, command):
    assert room.process_command(command, player) is None


def test_enter_sets_current_room(room, player, monkeypatch):
    feed_input(monkeypatch, ["go west"])
    room.enter(player)
    assert player.current_room == 14


# ---------------- standard commands ----------------

def test_get_and_drop(room, player):
    room.process_command("take pebble", player)
    assert player.has_item("pebble")
    room.process_command("drop pebble", player)
    assert not player.has_item("pebble")
    assert room.find_in_room("pebble") is not None


def test_objects_not_shared_between_rooms():
    a, b = Room(), Room()
    a.objects.clear()
    assert len(b.objects) == 1


def test_look_room_mentions_hole(room, player, capsys):
    room.process_command("look", player)
    assert "hole" in capsys.readouterr().out


def test_help_and_question_mark(room, player, capsys):
    room.process_command("help", player)
    room.process_command("?", player)
    assert capsys.readouterr().out.count("Commands") == 2


def test_hint(room, player, capsys):
    room.process_command("hint", player)
    assert "hole" in capsys.readouterr().out


def test_inventory_and_stats(room, player, capsys):
    room.process_command("take pebble", player)
    room.process_command("inventory", player)
    room.process_command("stats", player)
    out = capsys.readouterr().out
    assert "pebble" in out and "Health" in out


def test_quit_yes(room, player, monkeypatch):
    feed_input(monkeypatch, ["quit", "y"])
    assert room.enter(player) == "quit"


def test_quit_no_keeps_playing(room, player, monkeypatch):
    feed_input(monkeypatch, ["quit", "n", "go south"])
    assert room.enter(player) == "south"
