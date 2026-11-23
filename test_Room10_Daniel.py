from Room10_Daniel import Room
from player import Player


def make_player():
    return Player("Daniel", 100, "healthy", 0)


def test_room_number():
    room = Room()
    assert room.room_num == 10


def test_room_exits_match_map():
    room = Room()
    assert room.exits == ["east", "up", "down"]


def test_room_contains_key_and_chest():
    room = Room()
    assert room.get_item_from_object_list("key") is not None
    assert room.get_item_from_object_list("chest") is not None


def test_movement():
    room = Room()
    assert room.move("east") == "east"
    assert room.move("e") == "east"
    assert room.move("up") == "up"
    assert room.move("u") == "up"
    assert room.move("down") == "down"
    assert room.move("d") == "down"


def test_invalid_movement():
    room = Room()
    assert room.move("west") is None
    assert room.move("north") is None


def test_player_can_take_key():
    room = Room()
    player = make_player()

    room.get("key", player)

    assert player.has_item("key")
    assert room.get_item_from_object_list("key") is None


def test_key_unlocks_chest():
    room = Room()
    player = make_player()
    player.inventory.append(room.key)

    room.use("key", player)

    assert room.chest.state == "unlocked"


def test_chest_cannot_be_unlocked_without_key():
    room = Room()
    player = make_player()

    room.use("key", player)

    assert room.chest.state is False
