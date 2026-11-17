from Room8_jakob import Room


def test_room_description_names_the_forgotten_shrine():
    room = Room()

    assert "Forgotten Shrine" in room.description
