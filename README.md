# ![Random Bag](ui/icons/random_bag.ico) PaperMarioRandomizer ![Random Bag](ui/icons/random_bag.ico)

![](ui/images/random.png) ![](ui/images/peach.png)
![](ui/images/mistake.gif)

A randomizer for Paper Mario 64 using Star Rod (a modding tool by Clover) behind the scenes. It works by utilizing Star Rod to dump the game's contents, which it then parses through in text format to create data structures representing in-game objects like items, badges, key items, songs, sounds, loading zones, and so forth. These data structures are randomized and placed back into a form Star Rod recognizes, which are then used to compile the randomized ROM.
 
 Functional Features:
 - Item/Badge/KeyItem randomization
 - Song/Sound randomization
 - Loading Zone randomization (by all loading zones)
 - Ability to select which maps are included in randomization
 - Quality of Life options:
   - Action commands
   - Upgraded boots and hammer
   - All partners
   - All star spirits
   - "Warp to Home" ability, which allows Mario to travel to the warp pipe in Toad Town at any time

 Planned Features:
 - Loading Zone randomization (by area, e.g. only exits that lead to new areas would be randomized)
 - Smart Key Item randomization (implementing logic to prevent soft-locks)
 - Graphics randomization
 - Randomization stability (blacklisting certain maps and preventing crashes)
 
 How to Use:
 - Set up virtual environment with pipenv.
 - Running with Python: Run "pipenv run python main.py"
 - Editing GUI: Run "run_qt_designer.bat". This will open QtDesigner. Save changes or additions to the /ui folder.
 - Building executable: Run "build_exe.bat". The resulting executable will be in the /Release folder.
 - Note: Full release package must include StarRod folder and config.json in the same path as the executable.
 
 Currently, the project is in a mostly-working state but still needs a handful of tweaks and additions to be worthy of an official release package.

 
 
 
 
