import pyglet
import pymunk
from pymunk import Vec2d
from pymunk.pyglet_util import DrawOptions
from pyglet.window import key, mouse
import math
import time
RED = (220,20,30)
GREEN = (0,205,0)
options = DrawOptions()
destination = 0, 0
WIDTH, HEIGHT = 1280, 720
window = pyglet.window.Window(WIDTH, HEIGHT, "Game", resizable = False)
space = pymunk.Space()
class Laser(pymunk.Segment):
    def __init__(self, position, angle, color = GREEN):
        super().__init__(pymunk.Body(1, 100), (0, 0), (20, 0), 3)
        self.color = color
        self.sensor = True
        self.body.position = position
        self.body.angle = angle
        self.body.velocity = Vec2d(math.cos(self.body.angle), math.sin(self.body.angle)) * 800

class Ship(pymunk.Poly):
    def __init__(self):
        self.vertices = ((-75, 25), (0, 0), (-75, -25))
        super().__init__(None, (self.vertices))
        self.triangle_moment = pymunk.moment_for_poly(1, self.get_vertices())
        self.body = pymunk.Body(1, self.triangle_moment)
        self.position = WIDTH // 2, HEIGHT // 2
        self.laser_list = []
        self.cooldown = time.perf_counter()
    def shoot(self):
        if abs(self.cooldown - time.perf_counter()) >= (1/4):
            self.cooldown = time.perf_counter()
            self.laser_list.append(Laser(self.body.position, self.body.angle))
            space.add(self.laser_list[len(self.laser_list) - 1])
            space.add(self.laser_list[len(self.laser_list) - 1].body)

player = Ship()

space.add(player, player.body)
space.gravity = 0, 0

is_held_down = False

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.SPACE:
        global is_held_down
        is_held_down = True

@window.event
def on_key_release(symbol, modifiers):
    global is_held_down
    is_held_down = False

@window.event
def on_mouse_motion(x, y, dx, dy):
    global destination
    destination = x, y

@window.event
def on_draw():
    window.clear()
    space.debug_draw(options)

def refresh(time):
    if is_held_down == True:
        player.shoot()
    for i in player.laser_list:
        x_pos, y_pos = i.body.position
        if x_pos > WIDTH or x_pos < 0 or y_pos > HEIGHT or y_pos < 0:
            space.remove(i)
            space.remove(i.body)
            player.laser_list.remove(i)
            
    body_x, body_y = player.body.position
    x, y = destination
    player.body.angle = 0.0
    player.body.angle = player.body.angle + math.atan2(body_y - y, body_x - x) - (math.pi)
    distance = math.sqrt((x - body_x) ** 2 + (y - body_y) ** 2)
    if distance >= 10:
        player.body.velocity = Vec2d(math.cos(player.body.angle), math.sin(player.body.angle)) * 500
    else:
        player.body.velocity = 0, 0
    space.step(time)

if __name__ == "__main__":
    pyglet.clock.schedule_interval(refresh, 1.0/120.0)
    pyglet.app.run()