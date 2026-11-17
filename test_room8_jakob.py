from Room8_jakob import Room


def test_room_description_names_the_forgotten_shrine():
    room = Room()

    assert "Forgotten Shrine" in room.description


def test_room_has_a_visible_dying_bonfire():
    room = Room()

    assert room.objects[0].name == "Dying Bonfire"
    assert room.objects[0].visible
