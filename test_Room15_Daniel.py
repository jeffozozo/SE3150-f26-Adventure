import pytest
from unittest.mock import patch
from Room15_Daniel import Room
from player import Player
from object import Object

def make_player():
    return Player("Daniel", 100, "healthy", 0)

def describe_Room15_Daniel():

    def describe_initialization():
        
        def it_has_correct_room_number():
            room = Room()
            assert room.room_num == 4
            
        def it_has_correct_exits():
            room = Room()
            assert "west" in room.exits
            
        def it_contains_key_and_chest():
            room = Room()
            assert len(room.objects) == 2
            assert room.get_item_from_object_list("key") is not None
            assert room.get_item_from_object_list("chest") is not None

    def describe_movement():
        
        def it_returns_west_when_moving_west():
            room = Room()
            assert room.move("west") == "west"
            assert room.move("w") == "west"
            
        def it_returns_none_when_moving_invalid_direction():
            room = Room()
            assert room.move("east") is None

    def describe_interaction():

        def it_allows_player_to_take_key():
            room = Room()
            player = make_player()
            room.get("key", player)
            assert player.has_item("key")
            assert room.get_item_from_object_list("key") is None
            
        def it_unlocks_chest_when_using_key():
            room = Room()
            player = make_player()
            player.inventory.append(room.key)
            
            room.use("key", player)
            assert room.chest.state is True or room.chest.state == "unlocked"
            
        def it_cannot_unlock_chest_without_key():
            room = Room()
            player = make_player()
            
            room.use("key", player)
            assert room.chest.state is False or room.chest.state == "locked"
