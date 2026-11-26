from Room1_Kenneth import Room
from Room1_Kenneth import FragileHammer
from player import Player
from unittest.mock import patch
import pytest


# This stops the code from actually printing to console
@pytest.fixture(autouse=True)  # Got help from AI to figure this out
def mock_print():
    with patch("builtins.print") as mocked:
        yield mocked

def testRoomNumber():
    room = Room()
    assert room.room_num == 1

def testRoomExitsExists():
    room = Room()
    assert room.exits == ["north", "east", "down"]

# TODO Fix this test, Entering Room Changes Current Room
# def testEnteringRoomChangesPlayersCurrentRoom():
#     player = Player("Ken",100,"Fine","0")
#     room = Room()
#     room.enter(player)
#     assert player.current_room == 1
# Something I wanted to test but got stuck in the read from console and pytest did not like that.

def testSearchAddsHammerToInventory():
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.search(player, False)
    assert player.has_item("fragilehammer") == True

def testSearchGivesNothingOnSecondSearch():
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.search(player, True) # The True here is the flag that the room has already been searched once
    assert player.has_item("fragilehammer") == False

def testLookingAtDirectionOfExitPrintsTextToConsole(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.look(None, player, "on")
    room.look("north", player, "on")
    room.look("east", player, "on")
    room.look("down", player, "on")
    mock_print.call_count == 4

def testDescribeRoomPrintsToConsole(mock_print):
    room =Room()
    room.describe_room("on")
    mock_print.assert_called_once()

def testDropAddsItemToRoomInventory():
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "working", True)
    player.inventory.append(hamm)
    room.drop("fragilehammer",player)
    assert room.objects == [hamm]

def testDropWillPrintIfNoItemDropped(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.drop("fragilehammer",player)
    assert room.objects == [] # Make sure there is no objects in the room as well
    mock_print.assert_called_once()

def testDescribeRoomWillPrintTwiceWhenItemInRoom(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "working", True)
    player.inventory.append(hamm)
    room.drop("fragilehammer",player) # This works even when lower case, thank you .toLower
    room.describe_room("on")
    mock_print.call_count == 3

def testMoveRoomReturnsCorrectDirection(mock_print):
    room = Room()
    assert room.move("n") == "north" #"n","N","North","north"
    assert room.move("N") == "north"
    assert room.move("North") == "north"
    assert room.move("north") == "north"
    assert room.move("e") == "east" #"e","E","East","east"
    assert room.move("E") == "east"
    assert room.move("East") == "east"
    assert room.move("east") == "east"
    assert room.move("d") == "down" #"d","D","Down","down","hole","Hole","ladder","Ladder"
    assert room.move("D") == "down"
    assert room.move("Down") == "down"
    assert room.move("down") == "down"
    assert room.move("hole") == "down"
    assert room.move("Hole") == "down"
    assert room.move("ladder") == "down"
    assert room.move("Ladder") == "down"

def testMoveRoomReturnsNoneIfBadDirection(mock_print):
    room = Room()
    assert room.move("west") == None
    assert room.move("south") == None
    assert room.move("up") == None

def testUsingHammerBreaksIt(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "working", True)
    player.inventory.append(hamm)
    room.use("fragilehammer",player)
    assert player.get_item("fragilehammer").state == "broken"
    mock_print.call_count == 2 # Checks to make sure it prints when breaks vase, and prints on hammer use.

def testUsingBrokenHammerPrints(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "broken", True)
    player.inventory.append(hamm)
    room.use("fragilehammer",player)
    assert player.get_item("fragilehammer").state == "broken"
    mock_print.assert_called_once()

def testShowInventoryWithItemPresent(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "broken", True)
    player.inventory.append(hamm)
    room.show_inventory(player)
    mock_print.call_count == 2

def testShowInventoryWithMultipleItemsPresent(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "broken", True)
    player.inventory.append(hamm)
    player.inventory.append(hamm)
    room.show_inventory(player)
    mock_print.call_count == 3

def testShowInventoryWithNoItemsPresent(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.show_inventory(player)
    mock_print.assert_called_once()

def testShowStatsPrintsPlayerStatus(mock_print):
    player = Player("Ken",100,"Fine","0")
    room = Room()
    room.show_stats(player)
    mock_print.call_count == 5

def testShowHelpPrints(mock_print):
    room = Room()
    room.show_help()
    mock_print.assert_called_once()

def testShowHintPrints(mock_print):
    room = Room()
    room.show_hint()
    mock_print.assert_called_once()

def testUnknownCommandPrints(mock_print):
    room = Room()
    room.unknown_command()
    mock_print.assert_called_once()

def testGetItemFromInventoryReturnsItem():
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "broken", True)
    player.inventory.append(hamm)
    assert room.get_item_from_inventory("fragilehammer",player) == hamm

def testGetItemFromObjectListReturnsItem():
    player = Player("Ken",100,"Fine","0")
    room = Room()
    hamm = FragileHammer("FragileHammer", "A worn and fragile hammer, looks like it wll only be useful once.",True, "broken", True)
    room.objects.append(hamm)
    assert room.get_item_from_object_list("fragilehammer") == hamm