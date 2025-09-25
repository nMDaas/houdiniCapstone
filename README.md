# Image-Guided Terrain Generator for Unity Export (Houdini-Based tool)

When I first started learning game development in Unity, I loved experimenting with the Terrain Tools Package. It gave me a lot of freedom to shape the game world, but I quickly ran into a problem: it wasn’t easy to make a terrain that served a very specific gameplay idea, like building out a maze or a level with a strict design in mind. The tools were also non-procedural, which made iterating very slow and difficult.

This tool addresses these issues, providing accessibility to people who don’t use Houdini but still want a quick way to prototype and generate terrains that can drop right into Unity’s Terrain Tools workflow.

<p align="center">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/projectResults.png" object-fit="contain" width="500px" height="300px">
</p>

* Developed a Houdini shelf tool using Python, VEX, and Qt to supplement Unity’s Terrain Tools Package, enhancing customization in terrain design and surface detailing while making the workflow accessible to non-Houdini users in game development pipelines.
* Streamlined terrain prototyping and iteration by designing a step-by-step procedural workflow with image reload support and backtracking, providing an alternative to Unity’s non-procedural, constrained terrain workflow.
* Integrated height, surface detail, and water map inputs, enabling artists to define terrain elevation, surface characteristics, and water visualization for more deliberate, gameplay-driven terrain generation.
* Prepared terrains for OBJ export with adjustable LOD, enabling seamless integration into Unity’s Terrain Tools workflow for standard texturing, material assignment, and foliage placement.

## Demo
https://www.youtube.com/watch?v=FRj5c_c1SnM 

## Tool Workflow

### Overall Map-Driven Workflow
<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/toolWorkflow.png" width="500px" height=auto>
</p>

### Workflow for Terrain Elevation 
<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/terrainWorkflow.png" object-fit="contain" width="500px" height="300px">
</p>

<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/toutput1.png" object-fit="contain" width="500px" height="300px">
</p>

<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/toutput2.png" object-fit="contain" width="500px" height="300px">
</p>

## Tool Output Breakdown

<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/breakdown1.png" object-fit="contain" width="500px" height="300px">
</p>
<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/breakdown2.png" object-fit="contain" width="500px" height="300px">
</p>
<p align="left">
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/breakdown3.png" object-fit="contain" width="500px" height="300px">
</p>

## Unity Setup With Textures & Foliage
<img src="https://github.com/nMDaas/houdiniCapstone/blob/main/readmeContent/unityWorkflow.png" object-fit="contain" width="500px" height="300px">

## How to Use
- in houdini and then import to Unity

## External Resources Used

