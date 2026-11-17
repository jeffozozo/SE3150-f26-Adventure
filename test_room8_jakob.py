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
