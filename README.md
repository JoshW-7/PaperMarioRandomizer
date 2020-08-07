# PaperMarioRandomizer
 A randomizer for Paper Mario 64 using Star Rod (a modding tool by Clover) behind the scenes.
 
 Functional Features:
 - Item/Badge/KeyItem randomization
 - Song/Sound randomization
 - Loading Zone randomization (by all loading zones)
 - Ability to select which maps are included in randomization

 Planned Features:
 - Loading Zone randomization (by area, e.g. only exits that lead to new areas would be randomized)
 - Smart Key Item randomization (implementing logic to prevent soft-locks)
 - Quality of Life options (Start with upgraded Hammer/Boots, Star Spirits, Partners, etc)
 - Graphics randomization
 - Randomization stability (blacklisting certain maps and preventing crashes)
 
 How to Use:
 - Set up virtual environment with pipenv.
 - Running with Python: "python main.py"
 - Building executable: "build_exe.bat". The resulting executable will be in the /Release folder.
 - Note: Full release package must include StarRod folder and config.json in the same path as the executable.
 - Edit GUI by executing run_qt_designer. This will open QtDesigner. Save any UI changes or additions to the /ui folder.
 
 
 
 
