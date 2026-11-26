from unittest.mock import patch

from object import Object
from player import Player
from Room8_jakob import Room


def test_room_description_names_the_forgotten_shrine():
    room = Room()

    assert "Forgotten Shrine" in room.description


def test_room_has_a_visible_dying_bonfire():
    room = Room()

    assert room.objects[0].name == "Dying Bonfire"
    assert room.objects[0].visible


def test_room_keeps_a_direct_reference_to_the_bonfire():
    room = Room()

    assert room.bonfire is room.objects[0]


def test_all_room_objects_use_custom_object_classes():
    room = Room()

    for obj in room.objects:
        assert isinstance(obj, Object)
        assert type(obj) is not Object


def test_room_has_a_tombstone_with_a_bonfire_clue():
    room = Room()

    assert room.objects[1].name == "Weathered Tombstone"
    assert "ember" in room.objects[1].description.lower()


def test_room_has_a_sword_with_an_engraved_symbol():
    room = Room()

    assert room.objects[2].name == "Broken Knight's Sword"
    assert "symbol" in room.objects[2].description.lower()
    assert "flame symbol" in room.objects[1].description.lower()
    assert "flame symbol" in room.objects[2].description.lower()


def test_looking_at_tombstone_returns_its_clue():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    assert "hidden ember" in room.look("Weathered Tombstone", player)


def test_player_can_look_at_tombstone_by_short_name():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    assert "hidden ember" in room.look("tombstone", player)


def test_room_has_rusty_armor_with_a_story():
    room = Room()

    assert room.objects[3].name == "Rusty Armor"
    assert "knight" in room.objects[3].description.lower()


def test_room_has_ancient_ashes_by_the_bonfire():
    room = Room()

    assert room.objects[4].name == "Ancient Ashes"
    assert "bonfire" in room.objects[4].description.lower()


def test_looking_at_ashes_reveals_a_hidden_ember():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    ember = room.objects[5]

    assert ember.visible is False
    assert "ember" in room.look("Ancient Ashes", player).lower()
    assert ember.visible


def test_player_can_look_at_ashes_by_short_name():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    assert "hidden ember" in room.look("ashes", player).lower()
    assert room.objects[5].visible


def test_player_can_take_the_ember_after_finding_it():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    ember = room.objects[5]

    room.get("Ancient Ember", player)
    assert not player.has_item("Ancient Ember")

    room.look("Ancient Ashes", player)
    room.get("Ancient Ember", player)

    assert player.has_item("Ancient Ember")
    assert ember not in room.objects


def test_player_can_get_ember_by_short_name():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.look("ashes", player)

    room.get("ember", player)

    assert player.has_item("Ancient Ember")


def test_take_command_works_as_an_alias_for_get():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    with patch("builtins.input", side_effect=["look ashes", "take ember", "quit", "yes"]):
        room.enter(player)

    assert player.has_item("Ancient Ember")


def test_player_can_drop_the_ember_back_in_the_room():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    ember = room.objects[5]

    room.look("Ancient Ashes", player)
    room.get("Ancient Ember", player)
    room.drop("Ancient Ember", player)

    assert not player.has_item("Ancient Ember")
    assert ember in room.objects


def test_player_can_drop_ember_by_short_name():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.look("ashes", player)
    room.get("ember", player)

    room.drop("ember", player)

    assert not player.has_item("Ancient Ember")


def test_object_commands_accept_a_leading_the():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    assert "small flame" in room.look("the bonfire", player).lower()
    room.look("ashes", player)
    room.get("the ember", player)
    assert player.has_item("Ancient Ember")
    assert "small ember" in room.look("the ember", player).lower()
    room.drop("the ember", player)
    assert not player.has_item("Ancient Ember")


def test_using_the_bonfire_lights_it():
    room = Room()
    bonfire = room.objects[0]

    bonfire.use()

    assert bonfire.state == "lit"


def test_using_ember_lights_bonfire_and_consumes_ember():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    room.look("Ancient Ashes", player)
    room.get("Ancient Ember", player)
    room.use("ember on bonfire", player)

    assert room.objects[0].state == "lit"
    assert room.objects[0].name == "Bonfire"
    assert not player.has_item("Ancient Ember")
    assert "sealed" not in room.description.lower()
    assert room.move("east") == "east"
    assert room.move("up") == "up"


def test_using_the_ember_lights_the_bonfire():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.look("ashes", player)
    room.get("ember", player)

    room.use("the ember", player)

    assert room.objects[0].state == "lit"


def test_using_bonfire_without_ember_explains_what_is_needed():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    assert "need an ember" in room.use("bonfire", player).lower()


def test_using_lit_bonfire_or_ember_says_bonfire_is_already_lit():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.objects[0].use()

    assert "already lit" in room.use("bonfire", player).lower()
    assert "already lit" in room.use("the bonfire", player).lower()
    assert "already lit" in room.use("ember", player).lower()


def test_describing_room_uses_correct_object_grammar():
    room = Room()
    room.look("ashes", Player("Tester", 100, "healthy", 8))
    with patch("builtins.print") as printed:
        room.describe_room()

    lines = [call.args[0] for call in printed.call_args_list]
    assert "There are Ancient Ashes here." in lines
    assert "There is an Ancient Ember here." in lines


def test_bonfire_stays_unlit_without_an_ember():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    room.use("ember on bonfire", player)

    assert room.objects[0].state == "dying"


def test_player_can_look_at_an_item_in_inventory():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    room.look("Ancient Ashes", player)
    room.get("Ancient Ember", player)

    assert "small ember" in room.look("Ancient Ember", player)


def test_hint_points_to_the_tombstone_and_ember():
    room = Room()

    hint = room.hint().lower()

    assert "tombstone" in hint
    assert "ember" in hint
    assert "look at the ashes" in hint


def test_help_lists_the_room_commands():
    room = Room()

    help_text = room.help_text()

    assert "get" in help_text
    assert "take" in help_text
    assert "drop" in help_text
    assert "use" in help_text


def test_player_cannot_leave_until_bonfire_is_lit():
    room = Room()

    assert room.objects[0].state == "dying"
    assert room.move("east") is None
    assert room.move("up") is None


def test_looking_at_lit_bonfire_shows_its_state():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.objects[0].use()

    assert "lit" in room.look("Bonfire", player).lower()


def test_enter_sets_room_number_and_returns_selected_exit():
    room = Room()
    player = Player("Tester", 100, "healthy", 0)
    room.objects[0].use()

    with patch("builtins.input", return_value="go east"):
        next_direction = room.enter(player)

    assert player.current_room == 8
    assert next_direction == "east"


def test_move_command_works_as_an_alias_for_go():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    room.bonfire.use()

    with patch("builtins.input", return_value="move east"):
        next_direction = room.enter(player)

    assert next_direction == "east"


def test_enter_does_not_allow_exit_until_player_solves_puzzle():
    room = Room()
    player = Player("Tester", 100, "healthy", 0)

    commands = [
        "go east",
        "look ancient ashes",
        "get ancient ember",
        "use ember on bonfire",
        "go east",
    ]
    with patch("builtins.input", side_effect=commands):
        next_direction = room.enter(player)

    assert player.current_room == 8
    assert room.objects[0].state == "lit"
    assert next_direction == "east"


def test_confirmed_quit_returns_quit():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    with patch("builtins.input", side_effect=["quit", "yes"]):
        next_direction = room.enter(player)

    assert next_direction == "quit"


def test_declining_quit_keeps_playing():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    with patch("builtins.input", side_effect=["quit", "no", "quit", "yes"]):
        next_direction = room.enter(player)

    assert next_direction == "quit"


def test_player_cannot_move_north():
    room = Room()

    assert room.move("north") is None
