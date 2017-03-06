import my_globals as g
import database as db
import utility

def init():
    for i in range (0, 99):
        g.INVENTORY.append((db.InvItem.dic[""], 1))

def clear():
    for i in range (0, 99):
        g.INVENTORY[i] = (db.InvItem.dic[""], 1)

def add_item(item, quantity):
    """Looks for the nearest stack of the item and attempts to add the quantity and returns True. If none of the item are found, try to add the item and quantity to the nearest empty slot and return True. If the inventory is full, return False"""
    for i in range (0, 99):
        if g.INVENTORY[i][0].name == item:
            if g.INVENTORY[i][1] + quantity > db.InvItem.dic[item].limit:
                g.INVENTORY[i][1] = db.InvItem.dic[item].limit
            else:
                g.INVENTORY[i][1] += quantity
            return True
    for i in range (0, 99):
        if g.INVENTORY[i][0].name == "":
            g.INVENTORY[i] = (db.InvItem.dic[item], min(quantity, db.InvItem.dic[item].limit))
            return True
    return False
                
    
