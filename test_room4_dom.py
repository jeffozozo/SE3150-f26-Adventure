import pytest
from player import Player
from Room4_Dom import Room, GoldenHoleTrophy, MagnifyingGlass, STEPS_PER_WALL


@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return Player("Tester", 100, "healthy", 0)


def play(room, player, monkeypatch, commands):
    """Feeds the commands to room.enter() as fake keyboard input and returns what enter() returns."""
    inputs = iter(commands)

    def fake_input(prompt=""):
        try:
            return next(inputs)
        except StopIteration:
            raise AssertionError("Room asked for more input than the test provided")

    monkeypatch.setattr("builtins.input", fake_input)
    return room.enter(player)


WIN = ["play", "pose flamingo", "pose hourglass", "pose snake"]


# ---------- entering ----------

def test_enter_sets_current_room(room, player, monkeypatch):
    play(room, player, monkeypatch, ["quit", "y"])
    assert player.current_room == 4


def test_exits_match_map(room):
    assert sorted(room.exits) == ["down", "up"]


def test_room_starts_unsolved(room):
    assert room.solved is False
    assert room.walls_cleared == 0
    assert room.round_active is False


# ---------- exits ----------

def test_up_locked_before_solving(room, player, monkeypatch, capsys):
    result = play(room, player, monkeypatch, ["go up", "quit", "y"])
    assert result == "quit"
    assert "CHAMPIONS ONLY" in capsys.readouterr().out


def test_down_open_before_round(room, player, monkeypatch):
    assert play(room, player, monkeypatch, ["go down"]) == "down"
    assert player.health == 100


def test_down_shortcut(room, player, monkeypatch):
    assert play(room, player, monkeypatch, ["move d"]) == "down"


def test_down_during_round_forfeits_without_penalty(room, player, monkeypatch):
    result = play(room, player, monkeypatch, ["play", "pose flamingo", "go down"])
    assert result == "down"
    assert room.walls_cleared == 0
    assert room.round_active is False
    assert player.health == 100


def test_down_open_after_solving(room, player, monkeypatch):
    assert play(room, player, monkeypatch, WIN + ["go down"]) == "down"


def test_invalid_direction(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["go north", "quit", "y"])
    assert "You can't go that way." in capsys.readouterr().out


# ---------- winning ----------

def test_full_win_opens_up(room, player, monkeypatch):
    result = play(room, player, monkeypatch, WIN + ["go up"])
    assert result == "up"
    assert room.solved is True
    assert player.score == 50
    assert player.has_item("golden hole trophy")
    assert isinstance(player.get_item("golden hole trophy"), GoldenHoleTrophy)


def test_correct_pose_advances_and_resets_steps(room, player, monkeypatch):
    play(room, player, monkeypatch, ["play", "look", "pose flamingo", "quit", "y"])
    assert room.walls_cleared == 1
    assert room.steps_left == STEPS_PER_WALL


def test_reentry_after_solving_keeps_up_open(room, player, monkeypatch):
    play(room, player, monkeypatch, WIN + ["go up"])
    assert play(room, player, monkeypatch, ["go up"]) == "up"
    assert player.score == 50  # no second reward


def test_description_changes_after_solving(room, player, monkeypatch):
    before = room.description
    play(room, player, monkeypatch, WIN + ["go up"])
    assert room.description != before
    assert room.visible_exits() == ["up", "down"]


def test_play_after_solving_does_not_restart(room, player, monkeypatch):
    play(room, player, monkeypatch, WIN + ["play", "go up"])
    assert room.round_active is False


# ---------- failing ----------

def test_wrong_pose_pushes_down(room, player, monkeypatch):
    result = play(room, player, monkeypatch, ["play", "pose star"])
    assert result == "down"
    assert player.health == 90
    assert "wet" in player.condition
    assert room.walls_cleared == 0
    assert room.round_active is False


def test_fail_on_later_wall_resets_progress(room, player, monkeypatch):
    result = play(room, player, monkeypatch, ["play", "pose flamingo", "pose star"])
    assert result == "down"
    assert room.walls_cleared == 0


def test_wet_is_not_duplicated(room, player, monkeypatch):
    play(room, player, monkeypatch, ["play", "pose star"])
    play(room, player, monkeypatch, ["play", "pose star"])
    assert player.condition.count("wet") == 1
    assert player.health == 80


def test_running_out_of_steps_is_a_fail(room, player, monkeypatch):
    result = play(room, player, monkeypatch, ["play", "look", "inventory", "stats"])
    assert result == "down"
    assert player.health == 90
    assert "wet" in player.condition


def test_two_steps_is_not_yet_a_fail(room, player, monkeypatch):
    # two non-pose commands leave the wall 1 step away; confirmed quit leaves before a 3rd step
    play(room, player, monkeypatch, ["play", "look", "look", "quit", "y"])
    assert player.health == 100


def test_invalid_pose_uses_step_but_is_not_fail(room, player, monkeypatch):
    play(room, player, monkeypatch, ["play", "pose banana", "pose banana", "pose flamingo", "quit", "y"])
    assert room.walls_cleared == 1
    assert player.health == 100


def test_three_invalid_poses_is_a_fail(room, player, monkeypatch):
    result = play(room, player, monkeypatch, ["play", "pose banana", "pose banana", "pose banana"])
    assert result == "down"
    assert player.health == 90


def test_pose_without_round_does_nothing(room, player, monkeypatch):
    play(room, player, monkeypatch, ["pose flamingo", "quit", "y"])
    assert room.walls_cleared == 0
    assert player.health == 100


# ---------- objects ----------

def test_take_and_drop_magnifying_glass(room, player, monkeypatch):
    play(room, player, monkeypatch, ["take magnifying glass", "quit", "y"])
    assert player.has_item("magnifying glass")
    assert room.find_item("magnifying glass", room.objects) is None

    play(room, player, monkeypatch, ["drop glass", "quit", "y"])
    assert not player.has_item("magnifying glass")
    assert room.find_item("magnifying glass", room.objects) is not None


def test_prop_wall_cannot_be_taken(room, player, monkeypatch):
    play(room, player, monkeypatch, ["get prop wall", "quit", "y"])
    assert not player.has_item("prop wall")
    assert room.find_item("prop wall", room.objects) is not None


def test_magnifying_glass_does_not_use_a_step(room, player, monkeypatch, capsys):
    commands = ["take glass", "play",
                "use glass", "use glass", "use glass", "use glass",
                "pose flamingo", "quit", "y"]
    play(room, player, monkeypatch, commands)
    assert room.walls_cleared == 1
    assert player.health == 100
    assert "flamingo-esque" in capsys.readouterr().out


def test_magnifying_glass_outside_round(capsys):
    glass = MagnifyingGlass("magnifying glass", "desc", True, None, True)
    glass.use()
    assert "fingerprints" in capsys.readouterr().out


def test_magnifying_glass_clue_per_wall(capsys):
    glass = MagnifyingGlass("magnifying glass", "desc", True, 1, True)
    glass.use()
    assert "hourglass" in capsys.readouterr().out


def test_look_item_in_room(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["look prop wall", "quit", "y"])
    assert "foam wall" in capsys.readouterr().out


def test_look_missing_item(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["look banana", "quit", "y"])
    assert "You don't see that here." in capsys.readouterr().out


def test_trophy_travels_with_player(room, player, monkeypatch):
    play(room, player, monkeypatch, WIN + ["go up"])
    assert player.get_item("golden hole trophy").can_be_gotten is True


# ---------- other commands ----------

def test_quit_yes_returns_quit(room, player, monkeypatch):
    assert play(room, player, monkeypatch, ["quit", "y"]) == "quit"


def test_quit_no_stays_in_room(room, player, monkeypatch):
    assert play(room, player, monkeypatch, ["quit", "n", "go down"]) == "down"


def test_help_lists_poses_and_exits(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["help", "quit", "y"])
    out = capsys.readouterr().out
    assert "hourglass" in out
    assert "Exits: down" in out


def test_hint_is_room_specific(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["hint", "quit", "y"])
    assert "play" in capsys.readouterr().out


def test_talk_host_starts_round(room, player, monkeypatch):
    play(room, player, monkeypatch, ["talk host", "quit", "y"])
    assert room.round_active is True


def test_sherlock_speaks_on_entry(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["quit", "y"])
    assert "Sherlock:" in capsys.readouterr().out


def test_unknown_command(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["dance", "quit", "y"])
    assert "Command unavailable." in capsys.readouterr().out
