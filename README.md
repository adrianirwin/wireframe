# wireframe
Plugins/add-ons (currently only for Blender) to generate the geometry and UV maps needed to render a low-poly styled mesh asset as a pseudo-wireframe in a real-time context.

## Installation Instructions

### Blender Add-on
Move the entire `\blender-wireframe` folder from the `\plugins` so it is a sub-folder of the `Blender\\#.##\scripts\addons` folder. The exact location of the latter folder may vary based on the underlying operating system, but on Windows 10 it is `C:\Users\\[USER]\AppData\Roaming\Blender Foundation\Blender\\#.##\scripts\addons`

### UE4 Materials and Textures
There are three master materials in `\materials\ue4` folder, and a number of materials functions in the `\functions` sub-folder, that must be applied to an object to achieve the wireframe look. Simply copy the text content of each `.T3D` file and paste the contents into a newly created material in UE4.

The textures are straightforward, just import them as you would any other asset. Please note: the relationships between the materials and textures may need to be re-built.