from player import Player
from Room8_jakob import Room


def test_room_description_names_the_forgotten_shrine():
    room = Room()

    assert "Forgotten Shrine" in room.description


def test_room_has_a_visible_dying_bonfire():
    room = Room()

    assert room.objects[0].name == "Dying Bonfire"
    assert room.objects[0].visible


def test_room_has_a_tombstone_with_a_bonfire_clue():
    room = Room()

    assert room.objects[1].name == "Weathered Tombstone"
    assert "ember" in room.objects[1].description.lower()


def test_room_has_a_sword_with_an_engraved_symbol():
    room = Room()

    assert room.objects[2].name == "Broken Knight's Sword"
    assert "symbol" in room.objects[2].description.lower()


def test_looking_at_tombstone_returns_its_clue():
    room = Room()

    assert "hidden ember" in room.look("Weathered Tombstone")


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
    ember = room.objects[5]

    assert ember.visible is False
    assert "ember" in room.look("Ancient Ashes").lower()
    assert ember.visible


def test_player_can_take_the_ember_after_finding_it():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    ember = room.objects[5]

    room.get("Ancient Ember", player)
    assert not player.has_item("Ancient Ember")

    room.look("Ancient Ashes")
    room.get("Ancient Ember", player)

    assert player.has_item("Ancient Ember")
    assert ember not in room.objects


def test_player_can_drop_the_ember_back_in_the_room():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)
    ember = room.objects[5]

    room.look("Ancient Ashes")
    room.get("Ancient Ember", player)
    room.drop("Ancient Ember", player)

    assert not player.has_item("Ancient Ember")
    assert ember in room.objects


def test_using_the_bonfire_lights_it():
    room = Room()
    bonfire = room.objects[0]

    bonfire.use()

    assert bonfire.state == "lit"


def test_using_ember_lights_bonfire_and_consumes_ember():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    room.look("Ancient Ashes")
    room.get("Ancient Ember", player)
    room.use("ember on bonfire", player)

    assert room.objects[0].state == "lit"
    assert not player.has_item("Ancient Ember")


def test_bonfire_stays_unlit_without_an_ember():
    room = Room()
    player = Player("Tester", 100, "healthy", 8)

    room.use("ember on bonfire", player)

    assert room.objects[0].state == "dying"
