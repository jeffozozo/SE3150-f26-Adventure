from object import Object
from player import Player

class Brand(Object):
    def __init__(self):
        self.name = "brand"
        self.description = "A strange arcane symbol has been burned into the back of your left hand."
        self.can_be_gotten=False
        self.state="dormant"
        self.visible=True

    #just in case someone is using the brand
    def use(self):
        if self.state=="glowing":
            print("The brand on your left hand is glowing with a bright, ghoulish-green light.")
        else:
            print("The brand on your left hand aches, as if longing for the pedestals.")


class Room:
    def __init__(self):
        self.room_num=2
        self.description="A large stone room, filled with intricate arcane symbols lining every doorway,\nthere are even doorways in the ceiling and floor.\nIn the middle of the room lies 7 pedestals with hand prints.\n6 represent a door: up/down, or a cardinal direction (north, south, east, west).\nThe 7th lies in the middle, handprint glowing a dark red, and a plaque at the base with an inscription."
        self.riddle="A captain sets sail at dawn, welcoming the warm, golden sun.\nHe himself raises the colors high, a captain proud of his vessel and crew.\nHe looks behind him, knowing months may pass before he returns.\nThen looking ahead, he knows the sea holds many secrets waiting to be discovered!\nHe sails 'til dusk, the weary sun finally resting.\nBut the captain stays vigilant! For a ship only sleeps when it sinks into Davy Jones' Locker!"
        self.exits=[]
        self.closed_exits=['up','east','south','north','west','down']
        self.objects=[]
        self.order=['east','up','south','north','west','down']
        self.riddle_step=0

    def enter(self, player):
            player.current_room=self.room_num
            #introduction section
            b_check=player.get_item("brand")
            #if room puzzle is already done
            if b_check is not None and b_check.state=="glowing":
                self.exits=list(self.closed_exits)
                self.riddle_step=6
                print("Your brand still glows in a sickly spectral green. The doors recognize it, and stay open this time.")
            else:
            #when the player first enters, OR if for some reason someone discards the brand
                self.exits=[]
                self.riddle_step=0
                print("As you walk into the room, you hear the unmistakable sound of grinding stone. Then a loud thud echoes the chamber.\nAll exits are now sealed.")
            self.describe_room()

            while True:
                parts = input("> ").lower().split(maxsplit=1)
                if not parts:
                    continue
                command = parts[0]
                target = parts[1].strip() if len(parts) > 1 else ""
    
                if command in ["go", "move"]:
                    direction = self.move(target)
                    if direction is not None:
                        return direction
                    
                #touching pedestals
                elif command=="touch":
                    self.touch_pedestal(target,player)
                    if player.is_alive()==False:
                        return "quit"

                elif command == "look":
                    if not target:
                        self.describe_room()
                    elif target in ["plaque","riddle","words","inscription"]:
                        print("The inscription on the central pedestal's plaque says:\n"+str(self.riddle))
                    elif target in ["pedestal","pedestals","handprint"]:
                        print("The central pedestal has a recessed handprint, glowing a devilish red, and words inscribed on a plaque at the pedestal's base.")
                        print("Surrounding it are six other hand-pedestals for up, down, north, south, east, and west.")
                        print(str(self.riddle_step)+"/6 outer pedestals are glowing.")
                    else:
                        item=player.get_item(target)
                        if not item:
                            item = self.get_room_item(target)
                        if item:
                            print(item.description)
                            if item.state:
                                print("It is "+str(item.state)+".")
                        else:
                            print("Nothing to describe.")

                elif command=="use":
                    item=player.get_item(target) or self.get_room_item(target)
                    if item:
                        item.use()
                    else:
                        print("You can't use that.")

                elif command in ["get","take"]:
                    self.get(target,player)
                elif command in ["drop","put"]:
                    self.drop(target,player)
                elif command == "inventory":
                    player.show_inventory()
                elif command == "stats":
                    player.print_stats()
                elif command in ["help", "?"]:
                    print("Commands: go, move, touch [pedestal direction: central, up, down, north, south, east, west], look, inventory, stats, help, hint, quit")
                    print("Open Exits: " + ", ".join(self.exits))

                elif command=="hint":
                    if self.riddle_step!=6:
                        b_check=player.get_item("brand")
                        if not b_check:
                            print("That central pedestal has a handprint on it, maybe you should touch it?")
                        else:
                            print("The doors are still sealed, maybe the plaque has a clue?")
                            print("There is an order to the pedestals, you can just feel it!")
                            print(str(self.riddle_step)+"/6 outer pedestals are glowing.")
                    else:
                        print("Your brand glows brightly, and all doors are already open!")
                        print("Exits: "+", ".join(self.exits))

                elif command == "quit":
                    if input("Are you sure? (y/n) ").lower().startswith("y"):
                        player.print_stats()
                        return "quit"
                else:
                    print("Command unavailable.")

    def describe_room(self):
        print(self.description)
        if self.exits:
            print("Exits: " + ", ".join(self.exits))
        else:
            print("All doors are shut")
        if self.objects:
            print("There are items left on the ground:")
            for obj in self.objects:
                print(str(obj.name))
        
    def move(self,direction):
        direction = {"w": "west", "u": "up", "d": "down","e": "east","s": "south","n": "north"}.get(direction,direction)
        if direction in self.exits:
            return direction
        elif direction in self.closed_exits:
            print("Your brand hums as you get closer to the door, but it is still closed.")
            return None
        print("You can't go that way.")
        return None


    #picking up items
    def get_room_item(self,item_name):
        for item in self.objects:
            if item.name.lower()==item_name.lower():
                return item
        return None


    def get(self,item_name,player):
        if player.has_item(item_name):
            print("You already have "+str(item_name)+".")
            return
        item=self.get_room_item(item_name)
        if item is None:
            print(str(item_name)+" is not in the room.")
            return
        if not item.can_be_gotten:
            print(str(item.name)+" cannot be picked up")
            return
        player.inventory.append(item)
        self.objects.remove(item)
        print(str(item.name)+", is now in your inventory.")


    def drop(self,item_name,player):
        item=player.get_item(item_name)
        if item is None:
            print("You don't have "+str(item_name)+".")
            return
        if item.name.lower()=="brand":
            print("The brand is burned onto your skin, it can't be removed.")
            return
        player.inventory.remove(item)
        self.objects.append(item)
        print("You have dropped: "+str(item_name))
    

    def touch_pedestal(self,target,player):
        pedestal={"w": "west","u": "up","d": "down","e": "east","s": "south","n": "north","center": "center", "central": "center"}.get(target,target)
        b_check=player.get_item("brand")
        #central pedestal reactions
        if pedestal=="center":
            if b_check is not None and b_check.state=="glowing":
                print("The central pedestal glows a spectral green, along with your glowing brand.")
                print("You touch the pedestal, but the doors are already open! There is no effect.")
            elif b_check is not None:
                print("You touch the glowing-red central pedestal again. Suddenly the words on the plaque again speak into your mind:")
                print(self.riddle)
            else:
                print("You place your left hand into the glowing-red handprint on the central pedestal.")
                print("A stone pillar from the ceiling drops down abruptly on the pedestal, locking your hand into the pedestal.")
                print("Searing hot pain shoots through your arm, and a dark red glow seeps through the crack between the pillar and pedestal!")
                print("The pillar recedes back into the ceiling, like it never existed.")
                print("On the back of your hand is a symbol branded to your skin that strangely mirrors the pedestals locations in the room:")
                print("A diamond, representing the 4 cardinal directions, North, South, East, and West.\nSecond, is a vertical line with dots on the ends and middle,")
                print("the top represents up, the bottom represents down, and one in the middle, the central pedestal.")
                brand=Brand()
                player.inventory.append(brand)
                print("Suddenly the words on the plaque speak into your mind:")
                print(self.riddle)
            return

        #directional pedestal reactions
        if pedestal in self.order:
            if b_check is None:
                print("You place your left hand on the "+str(pedestal)+" pedestal, nothing happens.")
                return
            if b_check.state=="glowing":
                print("You place your glowing rune-branded hand on the "+str(pedestal)+" pedestal, nothing happens.")
                return
            step=self.order[self.riddle_step]
            if pedestal==step:
                self.riddle_step+=1
                print("You press your branded left hand on the "+str(pedestal)+" pedestal. The "+str(pedestal)+" pedestal glows a spectral green!")
                if self.riddle_step==6:
                    b_check.state="glowing"
                    b_check.description="A brand on your left hand that now glows a familiar spectral green."
                    self.exits=self.closed_exits
                    player.score+=1
                    print("Suddenly the earth rumbles, the stone doors opening all at once,")
                    print("and the central pedestal turns a familiar spectral green!")
                    print("You gained 1 point!")
                else:
                    print(str(self.riddle_step)+"/6 outer pedestals are now glowing.")
            else:
                player.health-=25
                print("You press your branded hand onto the "+str(pedestal)+" pedestal, but in the wrong order!")
                print("The brand erupts with a searing pain! -25 Health")
                if not player.is_alive():
                    print("The brand suddenly erupts into a crimson fire, incinerating you.")
        else:
            print("You can only choose a pedestal to touch: [central, north, south, east, west, up, down]")
