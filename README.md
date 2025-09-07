# Image-Guided Terrain Generator for Unity Export (Houdini-Based tool)

When I first started learning game development in Unity, I loved experimenting with the Terrain Tools Package. It gave me a lot of freedom to shape the world, but I quickly ran into a problem: it wasn’t easy to make a terrain that served a very specific gameplay idea, like building out a maze or a level with a strict design in mind. The tools were also non-procedural, which made iterating very slow and difficult.

This tool addresses these issues, providing accessibility to people who don’t use Houdini but still want a quick way to prototype and generate terrains that can drop right into Unity’s Terrain Tools workflow.

* Developed a Houdini shelf tool using Python, VEX, and Qt to supplement Unity’s Terrain Tools Package, enhancing customization in terrain design and surface detailing while making the workflow accessible to non-Houdini users in game development pipelines.
* Streamlined terrain prototyping and iteration by designing a step-by-step procedural workflow with image reload support and backtracking, providing an alternative to Unity’s non-procedural, constrained terrain workflow.
* Integrated height, surface detail, and water map inputs, enabling artists to define terrain elevation, surface characteristics, and water visualization for more deliberate, gameplay-driven terrain generation.
* Prepared terrains for OBJ export with adjustable LOD, enabling seamless integration into Unity’s Terrain Tools workflow for standard texturing, material assignment, and foliage placement.

## BREAKKKKKKKKKKKK

## Purpose of this Project
* Automate the workflow needed to set up an environment quickly - a lot of effort goes into “figuring stuff out” in Houdini
* Support the translation of a 2D visual of an environment to a 3D
  * Well documented so that a user does not need incredible knowledge of Houdini to use the tool
  * Give the power to a user to create what they have in their mind very quickly - important for bird’s eye view shots, very specific environment maps, game design environments

## Personal Goals
* Build onto my portfolio for a TD/tools pipeline position
* Get acquainted with another 3D industry standard software & learn its in & outs
* Learn how to build tools for Houdini

## View My Progress!
### Developed image to terrain workflows in Houdini
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/terrainWorkflow.png)
### GUI & UI/UX Sketches of Tool Interface
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/gui.png)

### Tool Progress: Converts Image to a Terrain in Houdini
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/toutput1.png)
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/toutput2.png)

### Developing Image to Flip Simulation Workflows in Houdini
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/woutput.png)

## Future Goals
* Finish programming tool so that the terrain/color map is easily editable in Houdini
  * Change in color
  * Change in color saturation
* Finalize workflow for creating the water body in the environment
* Start programming tool that generates a water body within the terrain
* Learn more about texturing a terrain and what that workflow looks like
* Iteratively work on GUI through user testing

## Inspiration
![Image of Key](https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/inspo.png)
