Squad High Resolution Map Extractor
======


Comparison with default
####

New:
![Preview](Sumari_AAS_v1_stitched.jpg)

Vanilla:
![Vanilla](https://squadmaps.com/full/Sumari_AAS_v1.jpg)

---

Requirements
 * [Squad SDK](https://squad.gamepedia.com/Squad_SDK#Downloading_the_Epic_Games_Launcher)
 * [Python 3.6+](https://www.python.org/)
    * [PIL](https://pypi.org/project/Pillow/) (pip install pillow)


---
Usage
1. Open up SDK, and open up a layer (_don't open master layer unless you know how to add lighting_) you want to render (_first time it will take a very long time_).

2. Open world properties and find minimap generation tool. Ingame minimaps have a resolution 4096 with a tile of 1. Increasing tiles will increase final resolution, however it might use up too much ram and crash if you choose a too large of a resolution-tile combo.

   __IMPORTANT!__ Before generating minimap tiles execute this command - `r.ViewDistanceScale.SecondaryScale 100` in the editor  to disable LOD optimizations so it renders all actors everything.


   ![Minimap tool](https://i.imgur.com/1BvNDQp.png "Minimap tool")

3. Create a master folder where you will keep all squad minimap generation folders (eg. SquadMinimaps). Create a folder __with the layer name__ (eg. Sumari_AAS_v1) within that master folder and export images from the minimap tool to that folder.

4. Copy `BP_FlagExport.uasset` into `{SquadEditor}\Squad\Content\Blueprints\Tools` (or any other folder) then inside the editor drag the copied blueprint into the viewport. In the world outliner select the added bp and under details fill out the necesary boxes. Use the same markers that you used when creating the minimap. Finaly, click on the generate json button.


   ![Settings](https://i.imgur.com/a2uSilC.png)

5. Copy json from `{SquadEditor}\Squad` directory into the directory you extracted your images to. Your folder should look something like this.

   ![Folder](https://i.imgur.com/jLvhANm.png)

6. Open `stitcher.py` and inside change the input/output settings (line 10 - 29). Run the script. If you did everything correctly there will be a generated image (formated as {layer}_stitched.jpg) in the same folder `IMG_DIR` folder.

---

TODO
###

Major
##
* ~~Fix flag zone rendring~~
* ~~Find out why the minimap tool only renders actors in the middle of the map and fix it~~ Fixed with `r.ViewDistanceScale.SecondaryScale 100`
* ~~Better json exporting - printing in console now~~
* ~~Map border export + rendering~~
* __Support more gamemodes (Only AAS tested)__

Minor
##
* GUI tool
* Multithreading
* Test non square maps (probably all minimaps are square but not sure)
* ~~Custom minimap rendering bluprint~~ Found fix for stock
   * ~~Connect both blueprints into a single tool~~
* Fully automate everything
* Finish documentation