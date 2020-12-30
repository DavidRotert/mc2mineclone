# mcimport
# a fork of the original 'mcimport' for the MineClone2 subgame.

This fork of mcimport converts a Minecraft world into Minetest; specifically a MineClone2 subgame.

## Notes

Compatible with Minecraft Worlds up to & including v1.12.2

This is a WIP; so the conversion list is continually being refined for more accurate conversions.

##### Coordinate Conversion from Minecraft to Minetest:
```
X = Approximately the same in both.
Y = Approximately -64 nodes in MCL2
Z = The number is approximately inverted.

Example:
Minecraft: -1457,4,-1632
Minetest-MineClone2: -1439,-60,1647
```

## MineClone 2 Info: 
* [Wuzzy's MineClone2 Sub-game forum link](https://forum.minetest.net/viewtopic.php?f=50&t=16407)
* [Wuzzy's MineClone2 Repo](http://repo.or.cz/MineClone/MineClone2.git)

--------------------------------------------------
The process is offline. Minecraft should not be running on the world
that is to be converted. The output should be an empty folder, and
no map.sqlite should be present in the empty folder.

The output is a world folder that is playable, permitted that you're using the MineClone2 sub-game.
This is a WIP, so you may still encounter "Unknown" blocks in the Minetest world.

This mcimport fork was created to improve on the existing mcimport
project, with one significant change: This form aims to create
*playable* minetest worlds where stuff works:

- chests can be used to put stuff in
- doors open and close
- simple mesecons circuits may work
- furnaces work

Also, the assumption is that converted maps are for multiplayer
use, and that the most important motivation for using this
converter is to *preserve* previously custom built objects
and buildings, but *not* meant to preserve the gameplay style
and feel of minecraft. This project aims to never convert
blocks to "Unknown" nodes and strives to leave a playable are
that is friendly for users performing a one-time conversion.

- some flowers are approximations
- double plants may end up being single node blocks
- until fixed, fences, walls & other items are likely broken


There are a large number of things that are just never going to
be convertable, and so the following will likely never work and
are therefore converted to air blocks. Entities are readily
spawned by several mob mods in minetest, so conversion is likely
not critical to users, and left out.


- entities

# Usage:

You'll need to use a Linux system and have python installed. The
easiest way to invoke the converter is to run the `mcimport.sh`
script without any parameters. This takes you through a bunch of
screens that you can use to select a world and configure a few
settings.

# License:

Copyright (C) 2017 - Nore, dgm555, sofar, MysticTempest, and others

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Except as contained in this notice, the name of the authors shall
not be used in advertising or otherwise to promote the sale, use or
other dealings in this Software without prior written authorization
from the authors.

