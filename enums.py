import os
import random

from items import item_type


def retrieve_enums(filepath):
    filenames = [filename for filename in os.listdir(filepath) if filename.endswith(".enum")]
    enums = {}
    for filename in filenames:
        with open(filepath + filename, "r") as file:
            enum = {
                "filename": filename,
                "name": "",
                "library": "",
                "reversed": None,
                "str": {},
            }
            for line in file.readlines():
                line = line.replace("\n", "").replace("\t", " ")
                if "% namespace" in line:
                    enum["name"] = line.split(" ")[0]
                elif "% library name" in line:
                    enum["library"] = line.split(" ")[0]
                elif "% reversed" in line:
                    enum["reversed"] = True if line.split(" ")[0] == "true" else False
                elif len(line) > 0 and not line.startswith("%"):
                    if line.find("%") != -1:
                        line = line[:line.find("%")]
                    tokens = [token for token in line.split(" ") if len(token) > 0]
                    if tokens:
                        if not enum["reversed"]:
                            hex_str = tokens[0]
                            name_str = tokens[-1]
                        else:
                            hex_str = tokens[-1]
                            name_str = tokens[0]
                        value = int(hex_str, 16)
                        enum["str"][name_str] = {
                            "previous_name": name_str,
                            "value": value,
                        }
            enums[enum["name"]] = enum
    return enums

def overwrite_enum(filepath, enum):
    with open(filepath + enum["filename"], "w") as file:

        enum["reversed"] = True

        file.write(f"{enum['name']} % namespace\n")
        file.write(f"{enum['library']} % library name\n")
        file.write(f"{'true' if enum['reversed'] else 'false'} % reversed\n")
        file.write("\n")
        for name,data in sorted(enum["str"].items(), key=lambda tup: tup[1]["value"]):
            hex_str = hex(data["value"])[hex(data["value"]).find("x")+1:].upper()
            if not enum["reversed"]:
                file.write(f"{hex_str} = {name} % {data['previous_name']}\n")
            else:
                file.write(f"{name} = {hex_str} % {data['previous_name']}\n")

def randomize_enum(enum, item_types=["Item", "Badge", "KeyItem", "Coin"]):
    if item_types != None:
        enum_data = enum["str"]
        values = [data["value"] for name,data in enum_data.items() if item_type(data["previous_name"]) in item_types]
        random.shuffle(values)
        for name,data in [(n,d) for n,d in enum_data.items() if item_type(d["previous_name"]) in item_types]:
            data["value"] = values.pop()
    else:
        enum_data = enum["str"]
        values = [data["value"] for name,data in enum_data.items()]
        random.shuffle(values)
        for name,data in enum_data.items():
            data["value"] = values.pop()
        
