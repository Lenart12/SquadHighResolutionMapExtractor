Squad High Resolution Map Extractor
======

Requirements
 * [Squad SDK](https://squad.gamepedia.com/Squad_SDK#Downloading_the_Epic_Games_Launcher)
 * [Python 3.6+](https://www.python.org/)
    * [PIL](https://pypi.org/project/Pillow/) (pip install pillow)

---
Workflow
1. Open up SDK, and open up a layer (_don't open master layer unless you know how to add lighting_) you want to render (_first time it will take a very long time_).

2. Open world properties and find minimap generation tool. Ingame minimaps have a resolution 4096 with a tile of 1. Increasing tiles will increase final resolution, however it might use up too much ram and crash if you choose a too large of a resolution-tile combo.
!(Minimap tool)[https://i.imgur.com/1BvNDQp.png "Minimap tool"]

3. Create a folder with the layer name and extract images from the minimap tool to that folder

4. Not finished WIP