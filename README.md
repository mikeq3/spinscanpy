# spinscanpy

This is a 3D laser scanner program written in python.

It was inspired by a program written in processing that was only able to run on a Apple Mac.
I wanted a program that would work on Linux and nobody had one. So I decided to write one.
This program spins a turntable powered by a servo connected to an arduino. It can control 
two lasers from different angles.
1 - The table is spun in record mode with one and then the other laser on.
	Two recordings can be made. One for mesh points and the other for texture.
2 - The recordings are then opened and an analysis is done to create the point cloud and map textures.
3 - The point cloud can then be brought into MeshLab and a solid 3D object can be formed. The object will have the surface color and texture from the scans.

This program worked at one time but currently needs work to get it working on the latest OpenGL
version.

Mike Q.
