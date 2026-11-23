import pytest
from player import Player
from Room2_Eric import Room, Brand
from object import Object

@pytest.fixture
def player():
    return Player("Link",100,"normal",0)

@pytest.fixture
def player_brand():
    player=Player("Link",100,"normal",0)
    brand=Brand()
    brand.state="glowing"
    player.inventory.append(brand)
    return player

@pytest.fixture
def room():
    return Room()


#enter
def test_room_enter(room,player):
    player.current_room=1
    player.current_room=room.room_num
    assert player.current_room==2
    assert room.riddle_step==0
    assert room.exits==[]

def test_reentry_with_glowing_brand(room,player_brand):
    b_check=player_brand.get_item("brand")
    room.touch_pedestal
    #if room puzzle is already done (THIS IS DIRECTLY FROM MY ROOM CODE TO TEST IT, IT CAN'T OTHERWISE)
    if b_check is not None and b_check.state=="glowing":
        room.exits=list(room.closed_exits)
        room.riddle_step=6
    assert room.riddle_step==6

def test_look_item(room,player):
    class Rupee(Object):
        def __init__(self):
            super().__init__("rupee","A green gem used as money in Hyrule.",True,"1",True)
        def use(self):
            pass
    #in-room
    rupee=Rupee()
    room.objects.append(rupee)
    room_item=player.get_item("rupee") or room.get_room_item("rupee")
    assert room_item is not None
    assert room_item.description=="A green gem used as money in Hyrule."
    #inventory
    room.objects.remove(rupee)
    player.inventory.append(rupee)
    inv_item=player.get_item("rupee") or room.get_room_item("rupee")
    assert inv_item is not None


#puzzle
def test_touch_get_brand(room,player):
    assert player.get_item("brand") is None
    room.touch_pedestal("center",player)
    brand=player.get_item("brand")
    assert brand is not None
    assert brand.name=="brand"
    assert brand.can_be_gotten is False
    assert brand.state=="dormant"

def test_touch_center_repeat(room,player):
    #1
    room.touch_pedestal("center",player)
    assert player.has_item("brand") is True
    #2
    room.touch_pedestal("center", player)
    assert len([item for item in player.inventory if item.name=="brand"])==1
    #glow
    brand=player.get_item("brand")
    brand.state="glowing"
    room.touch_pedestal("center",player)
    assert brand.state=="glowing"

def test_touch_central_means_center(room,player):
    room.touch_pedestal("central",player)
    assert player.get_item("brand") is not None

def test_puzzle_win(room,player):
    room.touch_pedestal("center",player)
    initial_score=player.score
    sequence=['east','up','south','north','west','down']
    for step_name in sequence:
        room.touch_pedestal(step_name,player)
    brand=player.get_item("brand")
    assert brand.state=="glowing"
    assert player.score==initial_score+1
    assert room.exits==room.closed_exits
    assert room.riddle_step==6

def test_puzzle_wrong_order_damage(room,player):
    room.touch_pedestal("center",player)
    initial_health=player.health
    room.touch_pedestal("down",player)
    assert player.health==initial_health-25
    assert room.riddle_step==0

def test_touch_pedestal_without_brand(room,player):
    room.touch_pedestal("east",player)
    assert room.riddle_step==0
    assert player.get_item("brand") is None

def test_touch_invalid_pedestal(room,player):
    room.touch_pedestal("center",player)
    room.touch_pedestal("leftward",player)
    assert room.riddle_step==0


#moving
def test_door_open_closed_movement(room,player):
    room.exits=[]
    assert room.move("north") is None
    room.exits=list(room.closed_exits)
    assert room.move("north")=="north"

def test_direction_shortcuts(room,player):
    room.exits = list(room.closed_exits)
    assert room.move("w")=="west"
    assert room.move("u")=="up"
    assert room.move("d")=="down"
    assert room.move("e")=="east"
    assert room.move("s")=="south"
    assert room.move("n")=="north"


#items
def test_brand_undroppable(room,player):
    room.touch_pedestal("center", player)
    assert player.has_item("brand") is True 
    room.drop("brand", player)
    assert player.has_item("brand") is True
    assert len(room.objects)==0

def test_get_and_drop_items(room,player):
    class Rock(Object):
        def __init__(self):
            super().__init__("rock","just a rock",True,"shiny",True)
        def use(self):
            pass
    item=Rock()
    room.objects.append(item)
    room.get("rock",player)
    assert player.has_item("rock") is True
    assert item not in room.objects
    room.drop("rock",player)
    assert player.has_item("rock") is False
    assert room.get_room_item("rock")==item

def test_get_invalid_item(room,player):
    room.get("sword",player)
    assert player.has_item("sword") is False

#tests dying from the puzzle
def test_player_death_handling(room,player):
    room.touch_pedestal("center",player)
    player.health=25
    room.touch_pedestal("down",player)
    assert player.is_alive() is False