# spinscanpy

This is a 3D laser scanner program written in python.

It was inspired by a program written in processing that was only able to run on an Apple Mac.
I wanted a program that would work on Linux and nobody had one so I decided to write one.
This program spins a turntable powered by a servo connected to an arduino. It can control 
two lasers from different angles.
1 - The table is spun in record mode with one laser and then the other laser enabled.
	Two recordings can be made. One for a point cloud and the other for texture.
2 - The recordings are then opened and an analysis is done to create the point cloud and map the textures.
3 - The point cloud can then be brought into MeshLab and a solid 3D object can be formed. The object will have the surface color and texture from the scans.

This program worked at one time but currently needs work to get it working on the latest OpenGL
version.

Mike Q.
