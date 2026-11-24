import pytest
from unittest.mock import MagicMock
from Room16_DayneWyler import Room, Object, ThrowingStone


def describe_room_16():
    @pytest.fixture
    def room():
        return Room()

    @pytest.fixture
    def player():
        mock_player = MagicMock()
        mock_player.health = 100
        mock_player.score = 0
        mock_player.condition = []
        mock_player.inventory = []
        return mock_player

    @pytest.fixture
    def feed_inputs(monkeypatch):
        """Simulate sequential user inputs; raises StopIteration instead of hanging."""
        def _feed(*responses):
            iterator = iter(responses)
            monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
        return _feed

    def describe_initialization():
        def it_sets_room_metadata_and_initial_puzzle_state(room):
            assert room.room_num == 16
            assert set(room.exits) == {"north", "south", "east", "west"}
            assert all(isinstance(obj, ThrowingStone) and isinstance(obj, Object) for obj in room.objects)
            assert [obj.name for obj in room.objects] == ["flint", "granite", "quartz", "slate", "pumice"]
            assert all(obj.state is None and obj.visible and obj.can_be_gotten for obj in room.objects)
            assert room.slots == [room.empty, room.empty, room.empty]
            assert room.trough == ["[ gold ]", "[ moss ]", "[ iron ]"]
            assert room.get_unlocked_cart() is None

    def describe_movement_commands():
        @pytest.mark.parametrize("command", ["go north", "move south"])
        def it_blocks_walking_and_tells_player_to_ride(room, player, feed_inputs, capsys, command):
            feed_inputs(command, "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "unlock and ride one of the minecarts" in output

    def describe_taking_and_dropping_items():
        ALL_STONES = ["flint", "granite", "quartz", "slate", "pumice"]

        @pytest.mark.parametrize("stone_name", ALL_STONES)
        def it_picks_up_each_individual_stone(room, player, feed_inputs, stone_name):
            feed_inputs(f"take {stone_name}", "quit", "y")
            room.enter(player)

            assert [obj.name for obj in player.inventory] == [stone_name]
            assert stone_name not in [obj.name for obj in room.objects]
            assert len(room.objects) == 4

        def it_picks_up_every_stone_one_by_one(room, player, feed_inputs):
            commands = [f"take {name}" for name in ALL_STONES] + ["quit", "y"]
            feed_inputs(*commands)
            room.enter(player)

            assert [obj.name for obj in player.inventory] == ALL_STONES
            assert room.objects == []

        def it_picks_up_the_first_stone_when_no_name_is_given(room, player, feed_inputs):
            feed_inputs("take", "quit", "y")
            room.enter(player)

            assert len(player.inventory) == 1
            assert isinstance(player.inventory[0], ThrowingStone)
            assert player.inventory[0].name == "flint"
            assert "flint" not in [obj.name for obj in room.objects]

        def it_picks_up_a_specific_stone_with_suffix(room, player, feed_inputs):
            feed_inputs("take quartz stone", "quit", "y")
            room.enter(player)

            assert len(player.inventory) == 1
            assert player.inventory[0].name == "quartz"
            assert "quartz" not in [obj.name for obj in room.objects]

        def it_picks_up_all_stones_at_once(room, player, feed_inputs):
            feed_inputs("take all", "quit", "y")
            room.enter(player)

            assert [obj.name for obj in player.inventory] == ALL_STONES
            assert room.objects == []

        @pytest.mark.parametrize("stone_name", ALL_STONES)
        def it_drops_each_individual_stone(room, player, feed_inputs, capsys, stone_name):
            feed_inputs(f"take {stone_name}", f"drop {stone_name}", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert f"You drop the {stone_name}." in output
            assert player.inventory == []
            assert stone_name in [obj.name for obj in room.objects]
            assert len(room.objects) == 5

        def it_drops_every_stone_one_by_one_after_taking_all(room, player, feed_inputs):
            commands = ["take all"] + [f"drop {name}" for name in ALL_STONES] + ["quit", "y"]
            feed_inputs(*commands)
            room.enter(player)

            assert player.inventory == []
            assert {obj.name for obj in room.objects} == set(ALL_STONES)

        def it_allows_re_taking_a_dropped_stone(room, player, feed_inputs):
            feed_inputs("take slate", "drop slate", "take slate", "quit", "y")
            room.enter(player)

            assert [obj.name for obj in player.inventory] == ["slate"]
            assert "slate" not in [obj.name for obj in room.objects]

        @pytest.mark.parametrize("stone_name", ALL_STONES)
        def it_handles_dropping_a_stone_not_in_inventory(room, player, feed_inputs, capsys, stone_name):
            feed_inputs(f"drop {stone_name}", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert f"You don't have the {stone_name}." in output
            assert player.inventory == []
            assert len(room.objects) == 5

        def it_handles_unknown_stone_names(room, player, feed_inputs, capsys):
            feed_inputs("take diamond", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "You don't see 'diamond' here." in output
            assert player.inventory == []

        def it_uses_a_stone_in_inventory(room, player, feed_inputs, capsys):
            feed_inputs("take flint", "use flint", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "You weigh the flint in your hand." in output

        def it_handles_using_a_stone_on_the_ground(room, player, feed_inputs, capsys):
            feed_inputs("use flint", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "You'll need to pick up the flint before you can use it." in output

        def it_handles_using_an_unknown_item(room, player, feed_inputs, capsys):
            feed_inputs("use diamond", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "you can't use that." in output

        def it_warns_when_no_stones_remain_on_the_ground(room, player, feed_inputs, capsys):
            feed_inputs("take all", "take", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "There are no loose stones left on the ground." in output
            assert len(player.inventory) == 5

        @pytest.mark.parametrize("command", ["grab stone", "get a rock", "pickup flint"])
        def it_supports_take_aliases_and_generic_stone_words(room, player, feed_inputs, command):
            feed_inputs(command, "quit", "y")
            room.enter(player)

            assert len(player.inventory) == 1
            assert player.inventory[0].name == "flint"
            assert "flint" not in [obj.name for obj in room.objects]

    def describe_switchboard_puzzle():
        @pytest.mark.parametrize(
            "slide_cmd, expected_cart",
            [
                ("slide iron 1", "plain"),
                ("slide moss 2", "over-grown"),
                ("slide gold 3", "gilded"),
                ("slide iron 2", "heavily damaged"),
            ],
        )
        def it_unlocks_the_matching_cart(room, player, feed_inputs, slide_cmd, expected_cart):
            feed_inputs(slide_cmd, "quit", "y")
            room.enter(player)

            assert room.get_unlocked_cart() == expected_cart

        def it_displaces_an_existing_artifact_back_to_the_trough(room, player, feed_inputs):
            feed_inputs("slide iron 1", "slide gold 1", "quit", "y")
            room.enter(player)

            assert room.slots[0] == "[ gold ]"
            assert "[ iron ]" in room.trough

        def it_removes_an_artifact_via_remove_or_take_slot(room, player, feed_inputs):
            feed_inputs("slide iron 1", "take slot 1", "quit", "y")
            room.enter(player)

            assert room.slots == [room.empty, room.empty, room.empty]
            assert "[ iron ]" in room.trough
            assert room.get_unlocked_cart() is None

        def it_resets_all_slots_and_restores_the_trough(room, player, feed_inputs):
            feed_inputs("slide iron 1", "slide moss 2", "reset", "quit", "y")
            room.enter(player)

            assert room.slots == [room.empty, room.empty, room.empty]
            assert room.trough == ["[ gold ]", "[ moss ]", "[ iron ]"]
            assert room.get_unlocked_cart() is None

    def describe_riding_minecarts():
        @pytest.mark.parametrize(
            "setup_cmds, ride_cmd, expected_direction",
            [
                (["slide iron 1"], "ride plain cart", "north"),
                (["slide iron 1"], "board basic minecart", "north"),
                (["slide iron 2"], "ride heavily damaged cart", "east"),
                (["slide iron 2"], "ride damaged", "east"),
            ],
        )
        def it_rides_unlocked_direct_carts(room, player, feed_inputs, setup_cmds, ride_cmd, expected_direction):
            feed_inputs(*setup_cmds, ride_cmd)
            result = room.enter(player)

            assert result == expected_direction
            assert player.current_room == 16

        @pytest.mark.parametrize(
            "setup_cmds, ride_cmd, expected_direction",
            [
                (["take flint", "slide moss 2"], "ride over-grown cart", "south"),
                (["take flint", "slide moss 2"], "ride overgrown", "south"),
                (["take flint", "slide gold 3"], "ride gilded cart", "west"),
                (["take flint", "slide gold 3"], "ride gold minecart", "west"),
            ],
        )
        def it_rides_lever_tracks_when_timing_and_stone_succeed(
            room, player, feed_inputs, setup_cmds, ride_cmd, expected_direction
        ):
            feed_inputs(*setup_cmds, ride_cmd, "hold", "throw")
            result = room.enter(player)

            assert result == expected_direction
            assert player.current_room == 16
            assert player.inventory == []
            assert player.score == 25

        def it_kills_the_player_on_the_east_track(room, player, feed_inputs):
            feed_inputs("slide iron 2", "ride damaged")
            result = room.enter(player)

            assert result == "east"
            assert player.health == 0
            assert "stuck in the bottom of a hole." in player.condition

        def it_boards_the_unlocked_cart_when_no_target_is_given(room, player, feed_inputs):
            feed_inputs("slide iron 1", "ride")
            result = room.enter(player)

            assert result == "north"

        def it_blocks_riding_when_all_carts_are_locked(room, player, feed_inputs, capsys):
            feed_inputs("ride", "ride plain cart", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "All four minecarts are locked to the tracks." in output
            assert "A heavy iron clamp locks it to the track." in output

        def it_rejects_invalid_carts_and_keeps_looping(room, player, feed_inputs, capsys):
            feed_inputs("slide iron 1", "ride rusty cart", "ride plain cart")
            result = room.enter(player)

            output = capsys.readouterr().out
            assert "Choose one of the minecarts:" in output
            assert result == "north"

    def describe_lever_sequence():
        def it_loops_back_when_throwing_too_early(room, player, feed_inputs, capsys):
            feed_inputs("take flint", "slide gold 3", "ride gilded", "throw", "quit", "y")
            result = room.enter(player)

            output = capsys.readouterr().out
            assert "too early" in output
            assert player.inventory == []
            assert result == "quit"

        def it_loops_back_when_holding_too_long(room, player, feed_inputs, capsys):
            feed_inputs("take flint", "slide moss 2", "ride overgrown", "hold", "hold", "quit", "y")
            result = room.enter(player)

            output = capsys.readouterr().out
            assert "You hold too long!" in output
            assert [obj.name for obj in player.inventory] == ["flint"]
            assert result == "quit"

        def it_loops_back_when_player_has_no_stones(room, player, feed_inputs, capsys):
            feed_inputs("slide gold 3", "ride gilded", "hold", "throw", "quit", "y")
            result = room.enter(player)

            output = capsys.readouterr().out
            assert "no stones to throw" in output
            assert result == "quit"

    def describe_looking_around():
        @pytest.mark.parametrize(
            "command, expected_text",
            [
                ("look", "abandoned minecart junction"),
                ("look switchboard", "ONE ARTIFACT ALIGNS ONE PATH"),
                ("look stones", "small stones"),
                ("look flint", "sharp-edged chunk of dark flint"),
                ("look flint", "The flint is on the ground."),
                ("look gilded cart", "gold-covered minecart"),
                ("look plain cart", "dirty, sturdy minecart"),
                ("look heavily damaged cart", "heavily dented minecart"),
                ("look over-grown cart", "vine-choked cart"),
                ("look tracks", "Heavy iron linkages"),
                ("look ceiling", "Nothing to describe."),
            ],
        )
        def it_describes_the_requested_target(room, player, feed_inputs, capsys, command, expected_text):
            feed_inputs(command, "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert expected_text in output

        def it_describes_a_stone_in_player_inventory(room, player, feed_inputs, capsys):
            feed_inputs("take quartz", "look quartz", "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "cloudy white chunk of quartz" in output
            assert "The quartz is in your inventory." in output

    def describe_player_and_utility_commands():
        def it_calls_player_inventory(room, player, feed_inputs):
            feed_inputs("inventory", "quit", "y")
            room.enter(player)

            player.show_inventory.assert_called_once()

        def it_calls_player_stats(room, player, feed_inputs):
            feed_inputs("stats", "quit", "y")
            room.enter(player)

            # Once for "stats", once on confirmed "quit"
            assert player.print_stats.call_count == 2

        def it_cancels_quit_when_user_says_no(room, player, feed_inputs):
            feed_inputs("quit", "n", "slide iron 1", "ride plain cart")
            result = room.enter(player)

            assert result == "north"
            player.print_stats.assert_not_called()

        def it_quits_when_user_confirms(room, player, feed_inputs):
            feed_inputs("quit", "y")
            result = room.enter(player)

            assert result == "quit"
            player.print_stats.assert_called_once()