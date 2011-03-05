import pyglet
from pyglet.gl import *

config = pyglet.gl.Config(alpha_size=8)
window = pyglet.window.Window(config=config)


class Camera(object):
    def __init__(self):
        self.fov = 65
        self.znear = .1
        self.zfar = 1000

        self.position = (0, 0, 0)
        self.

    def viewport_change(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, width / float(height), self.znear, self.zfar)
        glMatrixMode(GL_MODELVIEW)


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 0)
    glVertex2f(window.width, 0)
    glVertex2f(window.width, window.height)
    glEnd()

@window.event
def on_resize(width, height):
    camera.viewport_change(width, height)
    return pyglet.event.EVENT_HANDLED

@window.event
def on_key_press(symbol, modifiers):
    pass

@window.event
def on_mouse_press(x, y, button, modifiers):
    pass

@window.event
def on_mouse_motion(x, y, dx, dy):
    pass

pyglet.app.run()
