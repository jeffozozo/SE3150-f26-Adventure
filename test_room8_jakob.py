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
