import math

try:
	import OpenGL

	OpenGL.ERROR_CHECKING = False
	from OpenGL.GLU import gluPerspective
	from OpenGL.GL import *

	hasOpenGLlibs = True
except:
	print ("Failed to find PyOpenGL: http://pyopengl.sourceforge.net/")
	hasOpenGLlibs = False

def InitGL(window):
	# set viewing projection
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	size = window.GetSize()
	glViewport(0, 0, size.GetWidth(), size.GetHeight())

	#glLightfv(GL_LIGHT0, GL_POSITION, [0.2, 0.2, 1.0, 0.0])
	##glLightfv(GL_LIGHT1, GL_POSITION, [1.0, 1.0, 1.0, 0.0])

	#glEnable(GL_RESCALE_NORMAL)
	#glEnable(GL_LIGHTING)
	#glEnable(GL_LIGHT0)
	glEnable(GL_DEPTH_TEST)
	#glEnable(GL_CULL_FACE)
	#glDisable(GL_BLEND)
	glColorMaterial(GL_FRONT, GL_AMBIENT)
	glEnable(GL_COLOR_MATERIAL)

	glClearColor(0.0, 0.0, 0.0, 0.0)

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	aspect = float(size.GetWidth()) / float(size.GetHeight())
	gluPerspective(45.0, aspect, 1.0, 2000.0)


	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
	

def InitVLGL(window):
	# set viewing projection
	size = window.GetSize()
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glViewport(0, 0, size.GetWidth(), size.GetHeight())
	glClearColor(0.0, 0.0, 0.0, 0.0)
	glDisable(GL_DEPTH_TEST)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0, size.GetWidth(), 0, size.GetHeight(), -1.0, 1.0)
	glRasterPos2i(0, size.GetHeight() - 1)
	glPixelZoom(1.0, -1.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

