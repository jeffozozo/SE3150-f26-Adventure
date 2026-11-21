import pytest
from unittest.mock import MagicMock
from Room16_DayneWyler import Room


def describe_room_16():
    @pytest.fixture
    def room():
        return Room()

    @pytest.fixture
    def player():
        mock_player = MagicMock()
        mock_player.health = 100
        mock_player.condition = []
        return mock_player

    @pytest.fixture
    def feed_inputs(monkeypatch):
        """Simulate sequential user inputs; raises StopIteration instead of hanging."""
        def _feed(*responses):
            iterator = iter(responses)
            monkeypatch.setattr("builtins.input", lambda _prompt="": next(iterator))
        return _feed

    def describe_initialization():
        def it_sets_room_metadata(room):
            assert room.room_num == 16
            assert set(room.exits) == {"north", "south", "east", "west"}
            assert room.objects == []

    def describe_movement_commands():
        @pytest.mark.parametrize("command", ["go north", "move south"])
        def it_blocks_walking_and_tells_player_to_ride(room, player, feed_inputs, capsys, command):
            feed_inputs(command, "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert "must ride one of the minecarts" in output

    def describe_riding_minecarts():
        @pytest.mark.parametrize(
            "command, expected_direction",
            [
                ("ride plain cart", "north"),
                ("board basic minecart", "north"),
                ("ride over-grown cart", "south"),
                ("ride overgrown", "south"),
                ("ride gilded cart", "west"),
                ("ride gold minecart", "west"),
                ("ride heavily damaged cart", "west"),
                ("ride damaged", "west"),
            ],
        )
        def it_returns_the_mapped_direction(room, player, feed_inputs, command, expected_direction):
            feed_inputs(command)
            result = room.enter(player)

            assert result == expected_direction
            assert player.current_room == 16

        def it_prompts_for_a_cart_when_none_is_given(room, player, feed_inputs):
            feed_inputs("ride", "plain")
            result = room.enter(player)

            assert result == "north"

        def it_rejects_invalid_carts_and_keeps_looping(room, player, feed_inputs, capsys):
            feed_inputs("ride rusty cart", "ride plain cart")
            result = room.enter(player)

            output = capsys.readouterr().out
            assert "Must choose a valid cart" in output
            assert result == "north"

    def describe_looking_around():
        @pytest.mark.parametrize(
            "command, expected_text",
            [
                ("look", "abandoned minecart junction"),
                ("look gilded cart", "gold covered minecart"),
                ("look plain cart", "dirty and well-used minecart"),
                ("look heavily damaged cart", "heavily dented and battered"),
                ("look over-grown cart", "abandoned for 70 years"),
                ("look tracks", "tracks branch north"),
                ("look ceiling", "Nothing to describe."),
            ],
        )
        def it_describes_the_requested_target(room, player, feed_inputs, capsys, command, expected_text):
            feed_inputs(command, "quit", "y")
            room.enter(player)

            output = capsys.readouterr().out
            assert expected_text in output

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
            feed_inputs("quit", "n", "ride plain cart")
            result = room.enter(player)

            assert result == "north"
            player.print_stats.assert_not_called()

        def it_quits_when_user_confirms(room, player, feed_inputs):
            feed_inputs("quit", "y")
            result = room.enter(player)

            assert result == "quit"
            player.print_stats.assert_called_once()