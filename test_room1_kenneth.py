from Room1_Kenneth import Room
from player import Player

def test_room_number():
    room = Room()
    assert room.room_num == 1