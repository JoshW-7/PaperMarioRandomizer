import re
import os
import json
import xml.etree.ElementTree as ET

from items import item_value, item_type
from maps import Maps


class MapScript:

	# Dictionary to contain all MapScript instances, with keys being the filename (e.g. mac_00)
	scripts = {}

	def __init__(self, filepath):
		self.filepath = filepath
		self.filename = self.filepath.split('/')[-1].split('.')[0]
		self.nickname = ""
		self.area = self.filename.split("_")[0]

		xml_tree = ET.parse(self.filepath.split(self.filename)[0] + "../MapTable.xml")
		root = xml_tree.getroot()
		done = False
		for child in root.iter():
			if child.tag == "Area":
				for sub_child in child:
					if self.filename == sub_child.attrib["name"]:
						self.nickname = sub_child.attrib["nickname"]
						done = True
						break
			if done:
				break
				
		self.objects = {}
		self.track_enums = {}
		self.map_ascii = {}
		self.altered = False
		self.parse()
		MapScript.scripts[self.filename] = self

	def __str__(self):
		enum_list = ", ".join([f"{enum_name}:{amount}" for enum_name,amount in self.track_enums.items()])
		return f"<MapScript: {self.filename} - {self.nickname} - {enum_list}>"

	# Use to get a specific map by name
	# E.g. MapScript.get("mac_00")
	@classmethod
	def get(cls, key):
		return MapScript.scripts.get(key)

	# Get a list of unique area names (e.g. "mac", "tik", "jan", etc), but only from the list of MapScript instances passed in
	@classmethod
	def get_areas(cls, maps):
		unique_areas = set()
		for map_script in [map_script for map_script in maps]:
			unique_areas.add(map_script.area)
		return [area for area in unique_areas]

	# Convenience method to access this MapScript like a dictionary
	def __getitem__(self, object_name):
		return self.objects.get(object_name)

	# Search through the source script file and populate the objects dictionary
	def parse(self, track_enum_names=["Item", "Song", "Sound", "MapExit"]):
		self.track_enums = {name: 0 for name in track_enum_names}
		with open(self.filepath, "r") as file:
			reading_object = False
			object_name = ""
			object_type = ""

			# Populate the objects dictionary with each object in the map script
			for line in file.readlines():
				line = line.strip("\n")
				if line.startswith("#new"):
					reading_object = True
					object_type, object_name = line.split(":")[1:][0].split(" ")
					self.objects[object_name] = {
						"altered": False,
						"new": False,
						"type": object_type,
						"lines": [line],
					}
				elif not line.startswith("%") and not line.startswith("PADDING") and not line.startswith("MISSING") and object_name != "" and object_type != "" and reading_object:
					self.objects[object_name]["lines"].append(line)
				else:
					reading_object = False

			# Collect all enumerated values (Npc, Song, Item, Badge, KeyItem, etc) for each script object 
			for object_name,data in self.objects.items():
				for line_number,line in enumerate(data["lines"]):
					for match in [m for m in re.finditer(r"\.([^:]*):([^ ]*)( )?", line)]:
						enum_type = match.group(1)
						enum_name = match.group(2)
						if enum_type not in data:
							data[enum_type] = []
						data[enum_type].append({
							"object_name": object_name,
							"line_number": line_number,
							"type": enum_type,
							"name": enum_name,
							"value": item_value(enum_name),
							"item_type": item_type(enum_name),
							"original_name": enum_name,
							"original_value": item_value(enum_name),
							"original_item_type": item_type(enum_name),
							"shop_item": True if object_name.startswith("$ShopInventory") else False,
							"span": (
								line.find(f".{enum_type}:{enum_name}") + len(enum_type) + 2,
								line.find(f".{enum_type}:{enum_name}") + len(enum_type) + 2 + len(enum_name) + 1,
							)
						})
						if enum_type in track_enum_names:
							self.track_enums[enum_type] += 1

			# Collect GotoMap/GotoMapSpecial
			for object_name,data in self.objects.items():
				for line_number,line in enumerate(data["lines"]):
					matches = [m for m in re.finditer(r"GotoMapSpecial[ \t]+\([ \t]+([^ \t]*)[ \t]+([^ \t]*)[ \t]+[^ \t]+[ \t]+\)[ \t]+\%[ \t]+([^ \t]*)", line)]
					matches.extend([m for m in re.finditer(r"GotoMap[ \t]+\([ \t]+([^ \t]*)[ \t]+([^ \t]*)[ \t]+\)[ \t]+\%[ \t]+([^ \t]*)", line)])
					for match in matches:
						ascii_object = match.group(1)

						# This might be bad
						# TODO: Make it not bad
						try:
							entry_index = int(match.group(2), 16)
						except:
							entry_index = 0

						map_name = match.group(3)
						if "MapExit" not in data:
							data["MapExit"] = []
						data["MapExit"].append({
							"object_name": object_name,
							"line_number": line_number,
							"name": ascii_object,
							"map": map_name,
							"entry_index": entry_index,
							"span": (
								line.find(ascii_object),
								line.find(ascii_object) + len(ascii_object),
							)
						})
						if "MapExit" in track_enum_names:
							self.track_enums["MapExit"] += 1
					
			# Collect map ASCII strings
			for object_name,data in self.objects.items():
				if object_name.startswith("$ASCII"):
					text = data["lines"][2].replace("\t", "").replace('"', '')
					if text in Maps.get_maps():
						self.map_ascii[object_name] = text

	def replace_entity(self, enum_data, new_entity_name, global_enums):
		previous_name = enum_data["name"]
		enum_data["name"] = new_entity_name

		shop_item = False
		if enum_data["object_name"].startswith("$ShopInventory"):
			shop_item = True

		global_enums["Entity"]["str"][new_entity_name] = {
			"previous_name": previous_name,
			"value": global_enums["Entity"]["str"][previous_name]["value"],
			"shop_item": enum_data["shop_item"],
		}

		line_to_edit = self.objects[enum_data["object_name"]]["lines"][enum_data["line_number"]]
		line_to_edit = line_to_edit[0:enum_data["span"][0]] + enum_data["name"] + " " + line_to_edit[enum_data["span"][1]:]
		self.objects[enum_data["object_name"]]["lines"][enum_data["line_number"]] = line_to_edit

		enum_data["span"] = (
			line_to_edit.find(f".{enum_data['type']}:{enum_data['name']}") + len(enum_data['type']) + 2,
			line_to_edit.find(f".{enum_data['type']}:{enum_data['name']}") + len(enum_data['type']) + 2 + len(enum_data['type']) + 1,
		)
		self.altered = True
		self.objects[enum_data["object_name"]]["altered"] = True

	# Replace the specified item_type enums in this map script
	def replace_enum(self, enum_data, item_type, counter, global_enums):
		previous_name = enum_data["name"]
		enum_data["name"] = f"{item_type}_{counter:04d}"
		global_enums[item_type]["str"][f"{item_type}_{counter:04d}"] = {
			"previous_name": previous_name,
			"value": global_enums[item_type]["str"][previous_name]["value"]
		}

		line_to_edit = self.objects[enum_data["object_name"]]["lines"][enum_data["line_number"]]
		line_to_edit = line_to_edit[0:enum_data["span"][0]] + enum_data["name"] + " " + line_to_edit[enum_data["span"][1]:]
		self.objects[enum_data["object_name"]]["lines"][enum_data["line_number"]] = line_to_edit

		enum_data["span"] = (
			line_to_edit.find(f".{enum_data['type']}:{enum_data['name']}") + len(enum_data['type']) + 2,
			line_to_edit.find(f".{enum_data['type']}:{enum_data['name']}") + len(enum_data['type']) + 2 + len(enum_data['type']) + 1,
		)
		self.altered = True
		self.objects[enum_data["object_name"]]["altered"] = True

		counter += 1
		return counter

	# Replace all the GotoMap/GotoMapScpail calls' ASCII map with a string instead of the ASCII object
	# E.g.: Call GotoMap ( $ASCII_80242960 00000003 ) --> Call GotoMap ( "kmr_04" 00000003 )
	def replace_map_ascii(self):
		for e in self.get_exits():
			data = self.objects[e["object_name"]]
			line = data["lines"][e["line_number"]]
			match = re.search(r"(\$ASCII_[^ \t]*)[ \t]+([^ \t]*)", line)
			if match:
				# Replace the entry index
				start = match.span(2)[0]
				end = match.span(2)[1]
				line = line[0:start] + f"{e['entry_index']:08d}" + line[end:]

				# Replace the ASCII object label
				line = line.replace(match.group(1), f'\"{e["map"]}\"')
				data["lines"][e["line_number"]] = line
				data["altered"] = True

	# Get a list of enum data of a particular for this map script
	# Note that editing the values of the returned list will edit this map's object dictionary
	def get_enums(self, enum_type):
		enums = []
		for data in self.objects.values():
			if enum_type in data:
				enums.extend([enum_data for enum_data in data[enum_type]])
		return enums

	# Get a list of all the exits for this map script
	# Note that editing the values of the returned list will edit this map's object dictionary
	def get_exits(self):
		exits = []
		for data in self.objects.values():
			if "MapExit" in data:
				exits.extend(data["MapExit"])
		return exits

	# Export this map's object dictionary to JSON format (stored under /debug/map_script_objects/)
	def export_json(self):
		with open(f"./debug/map_script_objects/{self.filename}.json", "w") as file:
			json.dump(self.objects, file, indent=4)

	# Reconstruct the source script with the object dictionary and save as a map patch
	def create_mpat(self, filepath):
		with open(filepath + self.filename + ".mpat", "w") as file:
			for data in self.objects.values():
				if data["altered"]:
					if not data["new"]:
						data["lines"][0] = re.sub("#new:[^ ]*", "@", data["lines"][0])
					for line in data["lines"]:
						file.write(line + "\n")