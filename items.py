

ITEMS = {}
def retrieve_items():
    global ITEMS
    with open("./StarRod/MOD/globals/ItemTable.csv", "r") as file:
        lines = file.readlines()
        columns = {name.replace("\n", ""): i for i,name in enumerate(lines[0].split(","))}
        for line in lines[1:]:
            values = line.split(",")
            ITEMS[values[columns["Name"]].replace(" ", "")] = {column_name: values[columns[column_name]] for column_name in columns}

def item_value(item_name):
    global ITEMS
    if item_name in ITEMS:
        return int(ITEMS[item_name]["Index"], 16)
    else:
        return None
            
def item_type(item_name):
    value = item_value(item_name)
    if value:
        if value <= 0x7F:
            return "KeyItem"
        elif value > 0x7F and value <= 0xDF:
            return "Item"
        elif value > 0xDF and value <= 0x154:
            return "Badge"
        elif value == 0x157:
            return "Coin"
    return None