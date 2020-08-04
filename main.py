import os
import re
import sys
import time
import random
import psutil
import shutil
import threading
import subprocess

from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QCheckBox, QTableWidgetItem

from utilities import resource_path
from enums import retrieve_enums, overwrite_enum, randomize_enum
from items import ITEMS, retrieve_items, item_type, item_value
from maps import Maps

from map_script import MapScript


class GUI(QMainWindow):

	version = 0.4

	def __init__(self):
		super(GUI, self).__init__()
		uic.loadUi(resource_path("ui\\main_window.ui"), self)

		# Actions
		self.action_open.triggered.connect(self.open)

		# Buttons
		self.button_dump_rom.clicked.connect(self.dump)
		self.button_dump_rom.setEnabled(True)
		self.button_generate_objects.clicked.connect(self.generate)
		self.button_generate_objects.setEnabled(True)
		self.button_randomize.clicked.connect(self.randomize)
		self.button_compile_mod.clicked.connect(self.compile)

		self.button_check_selected.clicked.connect(self.check_selected)
		self.button_uncheck_selected.clicked.connect(self.uncheck_selected)

		try:
			rename_filepath = False
			with open("./StarRod/cfg/main.cfg", "r") as file:
				for line in file.readlines():
					if "RomPath = " in line:
						if "null" in line:
							self.button_dump_rom.setEnabled(False)
							self.button_generate_objects.setEnabled(False)
							break
		except:
			print("Could not open StarRod config file: main.cfg")

		if "globals" in os.listdir("./StarRod/MOD/"):
			self.button_dump_rom.setEnabled(False)
			self.button_generate_objects.setEnabled(True)
		else:
			self.button_generate_objects.setEnabled(False)

		self.show()

	def get_random_seed(self):
		items = [random.choice([re.sub(r"\d+", "", item) for item in ITEMS if item_type(item) == "Item"]) for i in range(4)]
		return "".join(items)

	def check_selected(self, state):
		for model_index in self.table_maps.selectionModel().selectedRows():
			self.table_maps.itemFromIndex(model_index).setCheckState(2)

	def uncheck_selected(self, state):
		for model_index in self.table_maps.selectionModel().selectedRows():
			self.table_maps.itemFromIndex(model_index).setCheckState(0)

	def maps_selected(self):
		checked_items = []
		for i in range(self.table_maps.rowCount()):
			if self.table_maps.item(i, 0).checkState() == 2:
				checked_items.append(self.table_maps.item(i, 0))

		return [MapScript.get(item.text().split("-")[0].replace(" ", "")) for item in checked_items]

	def open(self):
		options = QFileDialog.Options()
		filepath, _ = QFileDialog.getOpenFileName(self, "Choose ROM", "", "Vanilla PM64 ROM (*.z64)", options=options)
		if filepath:
			with open("./StarRod/cfg/main.cfg", "r") as file:
				lines = file.readlines()
			for i,line in enumerate(lines):
				if "RomPath = " in line:
					lines[i] = "RomPath = " + filepath.replace("/", "\\") + "\n"
					break
			with open("./StarRod/cfg/main.cfg", "w") as file:
				for line in lines:
					file.write(line)

			self.button_dump_rom.setEnabled(True)

	def update_log(self, message):
		self.listwidget_log.addItem(message)
		self.listwidget_log.scrollToBottom()
		QApplication.processEvents()

	def generate(self):
		self.button_generate_objects.setEnabled(False)

		# Copy original enum files to different directory
		if not os.path.exists("./StarRod/MOD/globals_enum_original/"):
			shutil.copytree("./StarRod/MOD/globals/enum/", "./StarRod/MOD/globals_enum_original/")

		# Get data from dumped content
		self.enums = retrieve_enums("./StarRod/MOD/globals_enum_original/")
		retrieve_items()
		Maps.retrieve_maps()

		# Generate MapScript objects for each .msrc file that was dumped
		self.map_scripts = []
		for filename in os.listdir("./StarRod/MOD/map/src/"):
			if filename.endswith(".mscr"):
				m = MapScript("./StarRod/MOD/map/src/" + filename)
				self.update_log(f"Generating: {m}")
				self.map_scripts.append(m)

		self.update_log("Finished generating MapScript objects. Ready to randomize.")

		# Add row for each map
		for m in self.map_scripts:
			self.table_maps.insertRow(self.table_maps.rowCount())
			item = QTableWidgetItem(f"{m.filename} - {m.nickname}")
			item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
			item.setCheckState(QtCore.Qt.Checked)
			self.table_maps.setItem(self.table_maps.rowCount()-1, 0, item)
			
		self.enable_widgets()
		self.text_seed.setText(self.get_random_seed())

	def dump(self):
		self.button_dump_rom.setEnabled(False)

		# Dump ROM assets
		folders = os.listdir("./StarRod/MOD/")
		self.can_randomize = True
		self.update_log("Dumping ROM...")
		
		if "globals" not in folders:
			self.can_randomize = False
			p = subprocess.Popen(["java", "-jar", "StarRod.jar", "-DumpAssets", "-CopyAssets"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="./StarRod/")
			display_text = False
			while True:
				line = p.stdout.readline().decode("utf-8")
				text = line[2:].rstrip("\n").replace("> ", "")
				if text.startswith("ERROR:"):
					display_text = True
				if len(text) > 1 and display_text:
					self.update_log(text)
				if "Creating mod directories..." in line:
					break
				QApplication.processEvents()
			self.can_randomize = True
			self.update_log("Finished dumping ROM.")

		# Copy original enum files to different directory
		if os.path.exists("./StarRod/MOD/globals_enum_original/"):
			shutil.rmtree("./StarRod/MOD/globals_enum_original/")
		shutil.copytree("./StarRod/MOD/globals/enum/", "./StarRod/MOD/globals_enum_original/")

		if self.can_randomize:
			self.button_dump_rom.setEnabled(False)
			self.button_generate_objects.setEnabled(True)

	def randomize(self):
		# Ensure fresh copy of dumped data
		if os.path.exists("./StarRod/MOD/globals/"):
			shutil.rmtree("./StarRod/MOD/globals/")
		p = subprocess.Popen(["java", "-jar", "StarRod.jar", "-CopyAssets"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="./StarRod/")
		display_text = True
		while True:
			line = p.stdout.readline().decode("utf-8")
			text = line[2:].rstrip("\n").replace("> ", "")
			if text.startswith("ERROR:"):
				display_text = True
			if len(text) > 1 and display_text:
				self.update_log(text)
			if "Creating mod directories..." in line:
				break
			QApplication.processEvents()

		# Set the seed based on what's in the textbox
		random.seed(a=self.text_seed.text(), version=2)

		# Only randomize maps that have been selected, and kmr_03 must be included
		maps = self.maps_selected()

		counter = {
			"item": 1,
			"song": 1,
			"sound": 1,
			"ambient_sound": 1,
		}
		for m in maps:
			# Overwrite all Items with unique values
			for enum_data in m.get_enums("Item"):
				counter["item"] = m.replace_enum(enum_data, "Item", counter["item"], self.enums)

			# Overwrite all Songs with unique values
			for enum_data in m.get_enums("Song"):
				counter["song"] = m.replace_enum(enum_data, "Song", counter["song"], self.enums)

			# Overwrite all Sounds with unique values
			for enum_data in m.get_enums("Sound"):
				counter["sound"] = m.replace_enum(enum_data, "Sound", counter["sound"], self.enums)

			# Overwrite all Ambient Sounds with unique values
			for enum_data in m.get_enums("AmbientSounds"):
				counter["ambient_sound"] = m.replace_enum(enum_data, "AmbientSounds", counter["ambient_sound"], self.enums)

		# Since we're starting in kmr_03 (skipping half the prologue or so), ensure story progress is set properly upon entering
		# This assumes "InitialMap = kmr_03" and "InitialEntry = Entry2" in mod.cfg
		kmr_03 = MapScript.get("kmr_03")
		kmr_03["$Script_Main_EnterWalk"]["lines"].insert(2, "\tIf *StoryProgress < FFFFFF86")
		kmr_03["$Script_Main_EnterWalk"]["lines"].insert(3, "\t\tSet *StoryProgress FFFFFF86")
		kmr_03["$Script_Main_EnterWalk"]["lines"].insert(4, "\tEndIf")
		kmr_03["$Script_Main_EnterWalk"]["altered"] = True
		kmr_03.altered = True

		# Randomize Loading Zones
		if self.chk_maps_loading_zone.isChecked():
			# Get a list of all the exits in the game
			all_exits = []
			for m in maps:
				all_exits.extend(m.get_exits())

			# Shuffle the exits, then loop over all the maps, changing each exit it has by popping one from the list of all exits
			random.shuffle(all_exits)
			for m in maps:
				for e in m.get_exits():
					other_exit = all_exits.pop()
					e["map"] = other_exit["map"]
					e["entry_index"] = other_exit["entry_index"]

				# Overwrite all ASCII in GotoMap calls with modified exit data
				m.replace_map_ascii()

		# Randomize Items (and coins)
		if self.chk_items.isChecked():
			item_types = ["Item"]
			if self.chk_coins.isChecked():
				item_types.append("Coin")
			randomize_enum(self.enums["Item"], item_types=item_types)

		# Randomize Badges
		if self.chk_badges.isChecked():
			randomize_enum(self.enums["Item"], item_types=["Badge"])

		# Randomize Key Items
		if self.chk_key_items.isChecked():
			randomize_enum(self.enums["Item"], item_types=["KeyItem"])

		# Randomize Songs
		if self.chk_music_loading_zone.isChecked():
			randomize_enum(self.enums["Song"], item_types=None, i_type="Song")

		# Randomize Sounds
		if self.chk_sounds.isChecked():
			randomize_enum(self.enums["Sound"], item_types=None, i_type="Sound")

		# Randomize Ambient Sounds
		if self.chk_ambient_sounds.isChecked():
			randomize_enum(self.enums["AmbientSounds"], item_types=None, i_type="AmbientSounds")

		# Overwrite the /globals/enum files with any changes
		overwrite_enum("./StarRod/MOD/globals/enum/", self.enums["Item"])
		overwrite_enum("./StarRod/MOD/globals/enum/", self.enums["Song"])
		overwrite_enum("./StarRod/MOD/globals/enum/", self.enums["Sound"])
		overwrite_enum("./StarRod/MOD/globals/enum/", self.enums["AmbientSounds"])

		# Delete any existing map patches
		for filename in os.listdir("./StarRod/MOD/map/patch/"):
			os.remove(f"./StarRod/MOD/map/patch/{filename}")

		# Create map patches for any map script that has been modified
		for m in maps:
			if m.altered:
				self.update_log(f"Creating Map Patch: {m}")
				m.create_mpat("./StarRod/MOD/map/patch/")
				m.export_json()

		# Ensure kmr_03 gets a map script if it wasn't selected for randomization (as it's the entry point for other modifications)
		if MapScript.get("kmr_03") not in maps:
			MapScript.get("kmr_03").create_mpat("./StarRod/MOD/map/patch/")
			MapScript.get("kmr_03").export_json()

		self.update_log("Finished Map Patches. Ready to compile mod.")
		self.button_compile_mod.setEnabled(True)

	def compile(self):
		# Tell Star Rod to compile the mod
		p = subprocess.Popen(["java", "-jar", "StarRod.jar", "-CompileMod"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd="./StarRod/")
		self.update_log("Compiling Mod...")
		display_text = False
		while True:
			line = p.stdout.readline().decode("utf-8")
			text = line[2:].rstrip("\n").replace("> ", "")
			if text.startswith("ERROR:"):
				display_text = True
			if len(text) > 1 and display_text:
				self.update_log(text)
			if "Mod compilation took" in line:
				break
			QApplication.processEvents()
		try:
			outs, errs = p.communicate(timeout=1)
		except subprocess.TimeoutExpired:
			p.kill()
			outs, errs = p.communicate()
		self.update_log("Finished compiling Mod")

		# Once Star Rod is finished, copy the ROM from the /out folder to wherever the user wants it to be
		files = os.listdir("./StarRod/MOD/out/")
		if len(files) > 0:
			options = QFileDialog.Options()
			filepath, _ = QFileDialog.getSaveFileName(self, "Save Randomized ROM", f"Paper Mario Randomized (V{self.version})", "(*.z64)", options=options)
			if filepath:
				shutil.copyfile("./StarRod/MOD/out/" + files[0], filepath)

	def enable_widgets(self, widget=None):
		if widget in [self.button_dump_rom, self.button_generate_objects, self.button_compile_mod]:
			return
		if widget is None:
			widget = self.centralwidget
		if hasattr(widget, "children"):
			if hasattr(widget, "setEnabled"):
				widget.setEnabled(True)
			for child in widget.children():
				self.enable_widgets(child)
		else:
			if hasattr(widget, "setEnabled"):
				widget.setEnabled(True)


app = QApplication(sys.argv)
gui = GUI()

app.exec_()