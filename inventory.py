import heapq

import my_globals as g
import database as db
import utility

def init():
    for i in range (0, g.INVENTORY_MAX_SLOTS):
        g.INVENTORY.append((db.InvItem.dic[""], 1))

def clear_all():
    for i in range (0, g.INVENTORY_MAX_SLOTS):
        clear_slot(i)

def clear_slot(slot):
    g.INVENTORY[slot] = (db.InvItem.dic[""], 1)

def find_item(key):
    for i in range(0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name == key:
            return i
        else:
            return -1

def add_item(item, quantity=1):
    """Looks for the nearest stack of the item and attempts to add the quantity and returns True. If none of the item are found, try to add the item and quantity to the nearest empty slot and return True. If the inventory is full, return False"""
    if quantity < 1:
        quantity = 1
    for i in range (0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name == item:
            if g.INVENTORY[i][1] + quantity > db.InvItem.dic[item].limit:
                newItem = db.InvItem.dic[item]
                newQuantity = db.InvItem.dic[item].limit
                g.INVENTORY[i] = (newItem, newQuantity)
            else:
                newItem = db.InvItem.dic[item]
                newQuantity = g.INVENTORY[i][1] + quantity
                g.INVENTORY[i] = (newItem, newQuantity)
            return True
    for i in range (0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name == "":
            g.INVENTORY[i] = (db.InvItem.dic[item], min(quantity, db.InvItem.dic[item].limit))
            return True
    return False

def remove_item(item, quantity=1):
    """Looks for the nearest stack of the item and attempts to remove the quantity and returns True. If none of the item are found, return False"""
    if quantity < 1:
        quantity = 1
    for i in range (0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name == item:
            if g.INVENTORY[i][1] <= quantity:
                clear_slot(i)
            else:
                newItem = db.InvItem.dic[item]
                newQuantity = g.INVENTORY[i][1]-quantity
                g.INVENTORY[i] = (newItem, newQuantity)
            return True
    return False

def consolidate():
    """Eliminate blank spaces while retaining the current order"""
    newList = []
    for i in range(0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name != "":
            newList.append(g.INVENTORY[i])
    clear_all()
    for i in range(0, len(newList)):
        g.INVENTORY[i] = newList[i]

def sort_by(sortKey):
    """Sort inventory based on the given key. Does not leave blank spaces"""
    heapQ = []
    heapq.heapify(heapQ)
    for i in range(0, g.INVENTORY_MAX_SLOTS):
        if g.INVENTORY[i][0].name != "":
            item = g.INVENTORY[i][0]
            quantity = g.INVENTORY[i][1]
            priority = item.sortPriority[sortKey]
            entry = (priority, item, quantity)
            heapq.heappush(heapQ, entry)
    clear_all()
    while heapQ:
        entry = heapq.heappop(heapQ)
        add_item(entry[1].name, entry[2])

def equip(hero, item, slot):
    #TODO check for full inventory

    invItem = db.InvItem.dic[item]
    if hero.equip[slot].name != "":
        add_item(hero.equip[slot].name)
    remove_item(item)
    hero.equip[slot] = invItem
