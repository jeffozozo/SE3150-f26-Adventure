import pytest
from player import Player
from object import Object
from Room11_AustinR import Room, Rope


class FakeLamp(Object):
    """A simple lamp for testing light mechanics."""
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


# Convenience for adding a lamp to the player
def add_lamp(player, state="on"):
    lamp = FakeLamp()
    lamp.state = state
    player.inventory.append(lamp)


# Win sequence: solve all three riddles
WIN = ["guess water", "guess stone", "guess flame"]


# ---------- entering ----------

def test_enter_sets_current_room(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["quit", "y"])
    assert player.current_room == 11


def test_exits_match_map(room):
    assert sorted(room.exits) == ["down", "north", "up"]


def test_room_starts_with_locked_door(room):
    assert room.door_locked is True
    assert room.current_puzzle == 0
    assert room.attempts == 0


# ---------- exits ----------

def test_north_locked_before_solving(room, player, monkeypatch, capsys):
    add_lamp(player)
    result = play(room, player, monkeypatch, ["go north", "quit", "y"])
    assert result == "quit"
    assert "locked tight" in capsys.readouterr().out


def test_north_open_after_solving(room, player, monkeypatch):
    add_lamp(player)
    assert play(room, player, monkeypatch, WIN + ["go north"]) == "north"


def test_up_always_open(room, player, monkeypatch):
    add_lamp(player)
    assert play(room, player, monkeypatch, ["go up"]) == "up"


def test_up_shortcut(room, player, monkeypatch):
    add_lamp(player)
    assert play(room, player, monkeypatch, ["move u"]) == "up"


def test_down_without_rope_hurts(room, player, monkeypatch):
    add_lamp(player)
    result = play(room, player, monkeypatch, ["go down"])
    assert result == "down"
    assert player.health == 80
    assert "bruised" in player.condition


def test_down_with_rope_safe(room, player, monkeypatch):
    add_lamp(player)
    result = play(room, player, monkeypatch, ["take rope", "go down"])
    assert result == "down"
    assert player.health == 100
    assert "bruised" not in player.condition


def test_bruised_not_duplicated(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["go down"])
    play(room, player, monkeypatch, ["go down"])
    assert player.condition.count("bruised") == 1
    assert player.health == 60


def test_invalid_direction(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["go west", "quit", "y"])
    assert "can't go that way" in capsys.readouterr().out


# ---------- winning ----------

def test_full_win_opens_door(room, player, monkeypatch):
    add_lamp(player)
    result = play(room, player, monkeypatch, WIN + ["go north"])
    assert result == "north"
    assert room.door_locked is False
    assert player.score == 45  # 10 + 10 + 10 + 15 bonus


def test_first_riddle_correct_advances(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess water", "quit", "y"])
    assert room.current_puzzle == 1
    assert room.attempts == 0
    assert room.history == []
    assert player.score == 10


def test_second_riddle_correct_advances(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess water", "guess stone", "quit", "y"])
    assert room.current_puzzle == 2
    assert player.score == 20


def test_third_riddle_correct_unlocks(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["quit", "y"])
    assert room.door_locked is False
    assert room.current_puzzle == 3
    assert player.score == 45


def test_description_changes_after_solving(room, player, monkeypatch):
    add_lamp(player)
    before = room.description
    play(room, player, monkeypatch, WIN + ["quit", "y"])
    assert room.description != before
    assert "open" in room.description


def test_reentry_after_solving_keeps_door_open(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["go north"])
    assert play(room, player, monkeypatch, ["go north"]) == "north"
    assert player.score == 45  # no second reward


def test_guess_after_solving_does_nothing(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["guess hello", "quit", "y"])
    assert "already open" in capsys.readouterr().out


# ---------- failing ----------

def test_wrong_guess_uses_attempt(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess hello", "quit", "y"])
    assert room.attempts == 1
    assert len(room.history) == 1
    assert player.health == 100  # not shocked yet


def test_six_wrong_guesses_shocks_and_resets(room, player, monkeypatch):
    add_lamp(player)
    commands = ["guess hello", "guess world", "guess fools", "guess beast", "guess human", "guess guest", "quit", "y"]
    play(room, player, monkeypatch, commands)
    assert room.attempts == 0
    assert room.history == []
    assert room.current_puzzle == 0  # stays on same riddle
    assert player.health == 90


def test_shock_never_drops_health_below_one(room, player, monkeypatch):
    player.health = 5
    add_lamp(player)
    commands = ["guess hello", "guess world", "guess fools", "guess beast", "guess human", "guess guest", "quit", "y"]
    play(room, player, monkeypatch, commands)
    assert player.health == 1


def test_wrong_then_correct_still_advances(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess hello", "guess world", "guess water", "quit", "y"])
    assert room.current_puzzle == 1
    assert player.score == 10


def test_invalid_length_does_not_use_attempt(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess hi", "quit", "y"])
    assert room.attempts == 0
    assert "five-letter" in capsys.readouterr().out


def test_non_alpha_does_not_use_attempt(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess 12345", "quit", "y"])
    assert room.attempts == 0
    assert "five-letter" in capsys.readouterr().out


# ---------- wordle scoring ----------

def test_score_guess_all_correct():
    marks = Room.score_guess("water", "water")
    assert marks == ["G", "G", "G", "G", "G"]


def test_score_guess_all_wrong():
    marks = Room.score_guess("hello", "water")
    assert marks == ["-", "Y", "-", "-", "-"]


def test_score_guess_mixed():
    marks = Room.score_guess("stare", "water")
    assert marks == ["-", "Y", "Y", "Y", "Y"]


def test_score_guess_repeated_letters():
    # guess has two 'e's but answer has only one
    marks = Room.score_guess("erase", "water")
    assert marks == ["-", "Y", "Y", "-", "G"]


def test_score_guess_exact_wins_over_yellow():
    marks = Room.score_guess("water", "water")
    assert marks == ["G", "G", "G", "G", "G"]


# ---------- darkness ----------

def test_dark_room_on_entry_without_lamp(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["quit", "y"])
    assert "pitch black" in capsys.readouterr().out


def test_cannot_read_tablet_in_dark(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["read tablet", "quit", "y"])
    assert "too dark" in capsys.readouterr().out


def test_cannot_guess_in_dark(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["guess water", "quit", "y"])
    assert "too dark" in capsys.readouterr().out


def test_cannot_look_room_features_in_dark(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["look door", "quit", "y"])
    assert "too dark" in capsys.readouterr().out


def test_can_move_in_dark(room, player, monkeypatch):
    # down doesn't require light
    result = play(room, player, monkeypatch, ["go down"])
    assert result == "down"


def test_can_look_at_carried_items_in_dark(room, player, monkeypatch, capsys):
    lamp = FakeLamp()
    lamp.state = "off"
    player.inventory.append(lamp)
    play(room, player, monkeypatch, ["look lamp", "quit", "y"])
    out = capsys.readouterr().out
    assert "turned on" in out or "off" in out


def test_turning_on_lamp_reveals_room(room, player, monkeypatch, capsys):
    lamp = FakeLamp()
    player.inventory.append(lamp)
    play(room, player, monkeypatch, ["use lamp", "quit", "y"])
    assert "Forgotten Cistern" in capsys.readouterr().out


def test_lamp_in_room_provides_light(room, player, monkeypatch, capsys):
    lamp = FakeLamp()
    lamp.state = "on"
    room.objects.append(lamp)
    play(room, player, monkeypatch, ["quit", "y"])
    assert "Forgotten Cistern" in capsys.readouterr().out


# ---------- objects ----------

def test_rope_starts_in_room(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["quit", "y"])
    assert room.get_item_from_object_list("rope") is not None


def test_take_and_drop_rope(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["take rope", "quit", "y"])
    assert player.has_item("rope")
    assert room.get_item_from_object_list("rope") is None

    play(room, player, monkeypatch, ["drop rope", "quit", "y"])
    assert not player.has_item("rope")
    assert room.get_item_from_object_list("rope") is not None


def test_rope_use_message(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["take rope", "use rope", "quit", "y"])
    assert "coil" in capsys.readouterr().out


def test_cannot_take_nonexistent_item(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["take banana", "quit", "y"])
    assert "not here" in capsys.readouterr().out


def test_already_have_item(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["take rope", "get rope", "quit", "y"])
    assert "already have" in capsys.readouterr().out


# ---------- look command ----------

def test_look_door_locked(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look door", "quit", "y"])
    assert "iron door" in capsys.readouterr().out


def test_look_door_unlocked(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["look door", "quit", "y"])
    assert "open" in capsys.readouterr().out


def test_look_stairs(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look stairs", "quit", "y"])
    assert "spiral" in capsys.readouterr().out


def test_look_shaft(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look shaft", "quit", "y"])
    assert "darkness" in capsys.readouterr().out


def test_look_tablet(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look tablet", "quit", "y"])
    assert "Riddle" in capsys.readouterr().out


def test_look_nothing(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look banana", "quit", "y"])
    assert "nothing like" in capsys.readouterr().out


def test_look_reprints_description(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["look", "quit", "y"])
    assert "Forgotten Cistern" in capsys.readouterr().out


# ---------- read command ----------

def test_read_tablet_shows_riddle(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["read tablet", "quit", "y"])
    assert "Riddle" in capsys.readouterr().out


def test_read_tablet_after_solving(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["read tablet", "quit", "y"])
    assert "gone dark" in capsys.readouterr().out


def test_read_invalid_target(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["read rope", "quit", "y"])
    assert "nothing like that" in capsys.readouterr().out


# ---------- other commands ----------

def test_quit_yes_returns_quit(room, player, monkeypatch):
    add_lamp(player)
    assert play(room, player, monkeypatch, ["quit", "y"]) == "quit"


def test_quit_no_stays_in_room(room, player, monkeypatch):
    add_lamp(player)
    assert play(room, player, monkeypatch, ["quit", "n", "go up"]) == "up"


def test_help_lists_commands_and_exits(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["help", "quit", "y"])
    out = capsys.readouterr().out
    assert "guess" in out
    assert "north" in out


def test_hint_without_lamp(room, player, monkeypatch, capsys):
    play(room, player, monkeypatch, ["hint", "quit", "y"])
    assert "lamp" in capsys.readouterr().out


def test_hint_with_lamp_off(room, player, monkeypatch, capsys):
    lamp = FakeLamp()
    player.inventory.append(lamp)
    play(room, player, monkeypatch, ["hint", "quit", "y"])
    assert "use lamp" in capsys.readouterr().out


def test_hint_with_door_locked(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["hint", "quit", "y"])
    assert "riddle" in capsys.readouterr().out


def test_hint_after_solving(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, WIN + ["hint", "quit", "y"])
    assert "rope" in capsys.readouterr().out


def test_inventory_command(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["inventory", "quit", "y"])
    assert "lamp" in capsys.readouterr().out


def test_stats_command(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["stats", "quit", "y"])
    out = capsys.readouterr().out
    assert "Health" in out or "health" in out


def test_unknown_command(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["dance", "quit", "y"])
    assert "can't do that" in capsys.readouterr().out


def test_empty_command_ignored(room, player, monkeypatch):
    add_lamp(player)
    # Empty strings should be ignored and not crash
    assert play(room, player, monkeypatch, ["", "", "go up"]) == "up"


# ---------- direction aliases ----------

def test_north_alias_n(room, player, monkeypatch):
    add_lamp(player)
    result = play(room, player, monkeypatch, WIN + ["go n"])
    assert result == "north"


def test_down_alias_d(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["take rope", "quit", "y"])
    result = play(room, player, monkeypatch, ["move d"])
    assert result == "down"


def test_shaft_alias(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["take rope", "quit", "y"])
    result = play(room, player, monkeypatch, ["go shaft"])
    assert result == "down"


# ---------- history tracking ----------

def test_history_shows_past_guesses(room, player, monkeypatch, capsys):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess hello", "guess world", "read tablet", "quit", "y"])
    out = capsys.readouterr().out
    assert "H E L L O" in out
    assert "W O R L D" in out


def test_history_clears_on_correct_answer(room, player, monkeypatch):
    add_lamp(player)
    play(room, player, monkeypatch, ["guess hello", "guess water", "quit", "y"])
    assert room.history == []


def test_history_clears_on_shock(room, player, monkeypatch):
    add_lamp(player)
    commands = ["guess hello", "guess world", "guess fools", "guess beast", "guess human", "guess guest", "quit", "y"]
    play(room, player, monkeypatch, commands)
    assert room.history == []