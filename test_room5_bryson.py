import pytest

from object import Object
from player import Player
from Room5_bryson import Room, Bat, Laptop, Button, CRASHED, BUTTON_REVEALED, TUNNEL_OPEN


class Lamp(Object):
    def use(self):
        pass


@pytest.fixture
def room():
    return Room()


@pytest.fixture
def player():
    return Player("tester", 100, "healthy", 0)


def type_commands(monkeypatch, commands):
    answers = iter(commands)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(answers))


def run(room, player, *commands):
    for command in commands:
        result = room.handle_command(command, player)
    return result


def solve_puzzle(room, player):
    run(room, player, "look rack", "get bat", "hit laptop", "use button")


def describe_room5():

    def describe_enter():

        def it_sets_current_room_to_5(room, player, monkeypatch):
            type_commands(monkeypatch, ["go west"])
            room.enter(player)
            assert player.current_room == 5

        def it_prints_the_room_on_entry(room, player, monkeypatch, capsys):
            type_commands(monkeypatch, ["go west"])
            room.enter(player)
            assert "server rack" in capsys.readouterr().out

        def it_keeps_reading_commands_until_the_player_leaves(room, player, monkeypatch):
            type_commands(monkeypatch, ["look", "dance", "", "go up"])
            assert room.enter(player) == "up"

        def it_returns_quit_when_the_player_confirms(room, player, monkeypatch, capsys):
            type_commands(monkeypatch, ["quit", "y"])
            assert room.enter(player) == "quit"
            assert "Health: 100" in capsys.readouterr().out

        def it_asks_for_confirmation_with_the_exact_prompt(room, player, monkeypatch):
            prompts = []

            def answer_yes(prompt=""):
                prompts.append(prompt)
                return "y"

            monkeypatch.setattr("builtins.input", answer_yes)
            assert run(room, player, "quit") == "quit"
            assert prompts == ["Are you sure? (y/n) "]

        def it_keeps_playing_when_the_player_declines_to_quit(room, player, monkeypatch, capsys):
            type_commands(monkeypatch, ["quit", "n", "go west"])
            assert room.enter(player) == "west"
            assert "Health:" not in capsys.readouterr().out

        def it_opens_the_tunnel_when_arriving_from_room_16(room, player, monkeypatch, capsys):
            player.current_room = 16
            type_commands(monkeypatch, ["go east"])
            assert room.enter(player) == "east"
            assert room.laptop.state == "dented"
            assert room.button.state == "pressed"
            assert player.score == 0
            assert player.current_room == 5
            output = capsys.readouterr().out
            assert "minecart rockets out of the tunnel" in output
            assert "hits the laptop" in output

        def it_keeps_the_tunnel_closed_when_arriving_from_elsewhere(room, player, monkeypatch):
            player.current_room = 10
            type_commands(monkeypatch, ["go east", "go west"])
            assert room.enter(player) == "west"
            assert room.puzzle_state == CRASHED

        def it_does_not_reopen_an_open_tunnel_from_room_16(room, player, monkeypatch, capsys):
            solve_puzzle(room, player)
            capsys.readouterr()
            player.current_room = 16
            type_commands(monkeypatch, ["go up"])
            room.enter(player)
            assert "minecart rockets out of the tunnel" not in capsys.readouterr().out
            assert player.score == 35

        def it_remembers_puzzle_progress_between_visits(room, player, monkeypatch):
            solve_puzzle(room, player)
            type_commands(monkeypatch, ["go east"])
            assert room.enter(player) == "east"

    def describe_move():

        def it_returns_west(room, player):
            assert run(room, player, "go west") == "west"

        def it_returns_up(room, player):
            assert run(room, player, "move up") == "up"

        def it_accepts_short_directions(room, player):
            assert run(room, player, "go w") == "west"
            assert run(room, player, "go u") == "up"

        def it_blocks_east_before_the_tunnel_opens(room, player, capsys):
            assert run(room, player, "go east") is None
            assert run(room, player, "go e") is None
            assert "stone wall" in capsys.readouterr().out

        def it_returns_east_after_the_tunnel_opens(room, player):
            solve_puzzle(room, player)
            assert run(room, player, "go east") == "east"
            assert run(room, player, "go e") == "east"

        def it_rides_the_minecart_east(room, player, capsys):
            solve_puzzle(room, player)
            capsys.readouterr()
            run(room, player, "go east")
            assert "minecart" in capsys.readouterr().out

        def it_rejects_directions_not_on_the_map(room, player, capsys):
            assert run(room, player, "go north") is None
            assert run(room, player, "go down") is None
            assert run(room, player, "go") is None
            assert "can't go that way" in capsys.readouterr().out

        def it_ignores_case_and_extra_spaces(room, player):
            assert run(room, player, "  GO   West  ") == "west"

    def describe_look():

        def it_prints_the_room_with_no_target(room, player, capsys):
            run(room, player, "look")
            output = capsys.readouterr().out
            assert "west" in output and "up" in output
            assert "There is a laptop here." in output

        def it_does_not_list_hidden_items(room, player, capsys):
            run(room, player, "look")
            output = capsys.readouterr().out
            assert "There is a bat here." not in output
            assert "There is a button here." not in output

        def it_shows_the_crashing_deployment_on_the_laptop(room, player, capsys):
            run(room, player, "look laptop")
            output = capsys.readouterr().out
            assert "0/47 pods ready" in output
            assert "The laptop is crashlooping." in output

        def it_shows_the_fixed_deployment_after_the_hit(room, player, capsys):
            run(room, player, "look rack", "get bat", "hit laptop")
            capsys.readouterr()
            run(room, player, "look laptop")
            output = capsys.readouterr().out
            assert "47/47 pods ready" in output
            assert "The laptop is dented." in output

        def it_reveals_the_bat_when_looking_at_the_rack(room, player, capsys):
            run(room, player, "look rack")
            assert room.bat.visible
            assert "you spot a bat" in capsys.readouterr().out

        def it_shows_items_in_the_inventory(room, player, capsys):
            player.inventory.append(Lamp("lamp", "A worn lamp.", True, "off", True))
            run(room, player, "look lamp")
            assert "A worn lamp." in capsys.readouterr().out

        def it_does_not_print_a_missing_state(room, player, capsys):
            player.inventory.append(Lamp("rope", "A sturdy rope.", True, None, True))
            run(room, player, "look rope")
            output = capsys.readouterr().out
            assert "A sturdy rope." in output
            assert "None" not in output

        def it_treats_hidden_items_as_not_there(room, player, capsys):
            run(room, player, "look button")
            assert "You don't see a button here." in capsys.readouterr().out

    def describe_get():

        def it_picks_up_the_bat_once_revealed(room, player):
            run(room, player, "look rack", "take bat")
            assert player.has_item("bat")
            assert room.bat not in room.objects

        def it_cannot_get_the_bat_while_hidden(room, player):
            run(room, player, "get bat")
            assert not player.has_item("bat")

        def it_cannot_take_the_laptop(room, player, capsys):
            run(room, player, "get laptop")
            assert not player.has_item("laptop")
            assert "can't take the laptop" in capsys.readouterr().out

        def it_cannot_take_the_button(room, player):
            run(room, player, "look rack", "get bat", "hit laptop", "get button")
            assert not player.has_item("button")

        def it_does_not_pick_up_an_item_twice(room, player, capsys):
            run(room, player, "look rack", "get bat", "get bat")
            assert len(player.inventory) == 1
            assert "already have the bat" in capsys.readouterr().out

        def it_asks_what_to_get_with_no_target(room, player, capsys):
            run(room, player, "get")
            assert "Get what?" in capsys.readouterr().out

    def describe_drop():

        def it_moves_the_item_into_the_room(room, player):
            run(room, player, "look rack", "get bat", "drop bat")
            assert not player.has_item("bat")
            assert room.bat in room.objects

        def it_lets_a_dropped_item_be_picked_up_again(room, player):
            run(room, player, "look rack", "get bat", "drop bat", "get bat")
            assert player.has_item("bat")

        def it_accepts_items_from_other_rooms(room, player):
            lamp = Lamp("lamp", "A worn lamp.", True, "off", False)
            player.inventory.append(lamp)
            run(room, player, "drop lamp", "get lamp")
            assert player.has_item("lamp")

        def it_reports_items_the_player_does_not_have(room, player, capsys):
            run(room, player, "drop sword")
            assert "You don't have a sword." in capsys.readouterr().out

        def it_asks_what_to_drop_with_no_target(room, player, capsys):
            run(room, player, "drop")
            assert "Drop what?" in capsys.readouterr().out

    def describe_puzzle():

        def it_starts_crashed(room):
            assert room.puzzle_state == CRASHED

        def it_reveals_the_button_when_the_laptop_is_hit(room, player):
            run(room, player, "look rack", "get bat", "hit laptop")
            assert room.puzzle_state == BUTTON_REVEALED
            assert room.button.visible
            assert room.laptop.state == "dented"

        def it_lets_use_bat_hit_the_laptop(room, player):
            run(room, player, "look rack", "get bat", "use bat")
            assert room.puzzle_state == BUTTON_REVEALED

        def it_accepts_hit_laptop_with_bat(room, player):
            run(room, player, "look rack", "get bat", "hit laptop with bat")
            assert room.puzzle_state == BUTTON_REVEALED

        def it_does_nothing_when_hitting_without_the_bat(room, player, capsys):
            run(room, player, "hit laptop")
            assert room.puzzle_state == CRASHED
            assert "does not care" in capsys.readouterr().out

        def it_requires_holding_the_bat_to_use_it(room, player, capsys):
            run(room, player, "look rack", "use bat")
            assert room.puzzle_state == CRASHED
            assert "need to be holding the bat" in capsys.readouterr().out

        def it_does_not_reveal_the_hidden_bat_when_used(room, player, capsys):
            run(room, player, "use bat")
            assert "You don't have a bat to use." in capsys.readouterr().out
            assert not room.bat.visible

        def it_only_hits_the_laptop(room, player, capsys):
            run(room, player, "look rack", "get bat", "hit rack")
            assert room.puzzle_state == CRASHED
            assert "won't help" in capsys.readouterr().out

        def it_asks_what_to_hit_with_no_target(room, player, capsys):
            run(room, player, "hit")
            assert "Hit what?" in capsys.readouterr().out

        def it_opens_the_tunnel_with_the_button(room, player):
            solve_puzzle(room, player)
            assert room.puzzle_state == TUNNEL_OPEN
            assert room.button.state == "pressed"
            assert "east" in room.available_exits()

        def it_cannot_use_the_button_before_it_is_revealed(room, player):
            run(room, player, "use button")
            assert room.puzzle_state == CRASHED

        def it_updates_the_description_when_the_tunnel_opens(room, player, capsys):
            solve_puzzle(room, player)
            capsys.readouterr()
            run(room, player, "look")
            output = capsys.readouterr().out
            assert "mining tunnel leading east" in output
            assert "minecart" in output

    def describe_score():

        def it_awards_10_for_hitting_the_laptop(room, player):
            run(room, player, "look rack", "get bat", "hit laptop")
            assert player.score == 10

        def it_awards_25_more_for_opening_the_tunnel(room, player):
            solve_puzzle(room, player)
            assert player.score == 35

        def it_does_not_award_score_twice(room, player, capsys):
            solve_puzzle(room, player)
            run(room, player, "hit laptop", "use bat", "use button")
            assert player.score == 35
            assert "already dented" in capsys.readouterr().out

        def it_never_changes_health_or_condition(room, player):
            solve_puzzle(room, player)
            run(room, player, "hit laptop", "hit rack")
            assert player.health == 100
            assert player.condition == ["healthy"]

    def describe_other_commands():

        def it_shows_the_inventory(room, player, capsys):
            run(room, player, "inventory")
            assert "Your inventory is empty." in capsys.readouterr().out

        def it_shows_the_stats(room, player, capsys):
            run(room, player, "stats")
            assert "Score: 0" in capsys.readouterr().out

        def it_lists_commands_and_current_exits_in_help(room, player, capsys):
            run(room, player, "help")
            output = capsys.readouterr().out
            assert "hit" in output
            assert "Exits: west, up" in output
            assert "east" not in output

        def it_accepts_question_mark_for_help(room, player, capsys):
            run(room, player, "?")
            assert "Commands:" in capsys.readouterr().out

        def it_shows_east_in_help_once_open(room, player, capsys):
            solve_puzzle(room, player)
            capsys.readouterr()
            run(room, player, "help")
            assert "Exits: west, up, east" in capsys.readouterr().out

        def it_gives_a_hint_for_each_puzzle_step(room, player, capsys):
            hints = []
            for step in ["look rack", "hit laptop", "use button"]:
                run(room, player, "hint")
                hints.append(capsys.readouterr().out)
                run(room, player, step)
                if step == "look rack":
                    run(room, player, "get bat")
                capsys.readouterr()
            run(room, player, "hint")
            hints.append(capsys.readouterr().out)

            assert "hiding something" in hints[0]
            assert "harder" in hints[1]
            assert "Big red buttons" in hints[2]
            assert "tunnel east is open" in hints[3]

        def it_shows_the_kubectl_screen_when_using_the_laptop(room, player, capsys):
            run(room, player, "use laptop")
            assert "CrashLoopBackOff" in capsys.readouterr().out

        def it_asks_what_to_use_with_no_target(room, player, capsys):
            run(room, player, "use")
            assert "Use what?" in capsys.readouterr().out

        def it_reports_items_that_cannot_be_used(room, player, capsys):
            run(room, player, "use sword")
            assert "You don't have a sword to use." in capsys.readouterr().out

        def it_handles_unknown_commands(room, player, capsys):
            assert run(room, player, "dance") is None
            assert "help" in capsys.readouterr().out

        def it_handles_empty_input(room, player, capsys):
            assert run(room, player, "   ") is None
            assert "help" in capsys.readouterr().out

    def describe_objects():

        def it_has_objects_that_subclass_object():
            for cls in [Bat, Laptop, Button]:
                assert issubclass(cls, Object)

        def it_swings_the_bat(capsys):
            Bat("bat", "", True, "intact", True).use()
            assert "practice swing" in capsys.readouterr().out

        def it_shows_the_crash_screen_on_a_crashing_laptop(capsys):
            Laptop("laptop", "", False, "crashlooping", True).use()
            assert "CrashLoopBackOff" in capsys.readouterr().out

        def it_shows_running_pods_on_a_dented_laptop(capsys):
            Laptop("laptop", "", False, "dented", True).use()
            assert "All pods Running" in capsys.readouterr().out

        def it_presses_the_button():
            button = Button("button", "", False, "unpressed", True)
            button.use()
            assert button.state == "pressed"

        def it_starts_each_room_with_its_own_objects():
            first, second = Room(), Room()
            assert first.objects is not second.objects
            assert len(second.objects) == 3
