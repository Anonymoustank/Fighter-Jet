import pyglet
import pymunk
from pymunk import Vec2d
from pymunk.pyglet_util import DrawOptions
from pyglet.window import key, mouse
import math
import time
import random
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
        self.damage = 25

class Ship(pymunk.Poly):
    def __init__(self, color = GREEN, laser_type = "default"):
        self.vertices = ((-50, 25), (0, 0), (-50, -25))
        super().__init__(None, (self.vertices))
        self.triangle_moment = pymunk.moment_for_poly(1, self.get_vertices())
        self.body = pymunk.Body(1, self.triangle_moment)
        self.position = WIDTH // 2, HEIGHT // 2
        self.laser_list = []
        self.cooldown = time.perf_counter()
        self.sensor = True
        self.color = color
        self.health = 100
        self.laser_type = laser_type
    def shoot(self):
        if self.laser_type == "three-shooter":
            if abs(self.cooldown - time.perf_counter()) >= (1/3):
                self.cooldown = time.perf_counter()
                self.laser_list.append(Laser(self.body.position, self.body.angle))
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)
                self.laser_list.append(Laser(self.body.position, self.body.angle + math.pi/20))
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)
                self.laser_list.append(Laser(self.body.position, self.body.angle - math.pi/20))
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)
        elif self.laser_type == "default":
            if abs(self.cooldown - time.perf_counter()) >= (1/6):
                self.cooldown = time.perf_counter()
                variance = random.uniform(-1 * math.pi/25, math.pi/25)
                self.laser_list.append(Laser(self.body.position, self.body.angle + variance))
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)

player = Ship(GREEN, "three-shooter")
enemy_list = []
for i in range(1):
    enemy_list.append(Ship(RED, "default"))
    space.add(enemy_list[len(enemy_list) - 1])
    space.add(enemy_list[len(enemy_list) - 1].body)
    enemy_list[len(enemy_list) - 1].body.position = WIDTH // 2, HEIGHT // 2

dead = False

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
    global dead
    if is_held_down == True:
        player.shoot()
    if dead == False:
        for i in player.laser_list:
            for enemy in enemy_list:
                if len(i.shapes_collide(enemy).points) > 0:
                    enemy.health -= i.damage
                    if enemy.health <= 0:
                        space.remove(enemy)
                        space.remove(enemy.body)
                        enemy_list.remove(enemy)
                    space.remove(i)
                    space.remove(i.body)
                    player.laser_list.remove(i)
            x_pos, y_pos = i.body.position
            if x_pos > WIDTH or x_pos < 0 or y_pos > HEIGHT or y_pos < 0:
                space.remove(i)
                space.remove(i.body)
                player.laser_list.remove(i)
    if dead == False and len(enemy_list) > 0:
        for i in enemy_list:
            body_x, body_y = i.body.position
            x, y = player.body.position
            i.body.angle = 0.0
            i.body.angle = i.body.angle + math.atan2(body_y - y, body_x - x) - (math.pi)
            distance = math.sqrt((x - body_x) ** 2 + (y - body_y) ** 2)
            if distance >= 200:
                i.body.velocity = Vec2d(math.cos(i.body.angle), math.sin(i.body.angle)) * 450
            else:
                i.body.velocity = 0, 0

    if dead == False:
        for enemy in enemy_list:
            for enemy_laser in enemy.laser_list:
                if len(enemy_laser.shapes_collide(player).points) > 0:
                    player.health -= enemy_laser.damage
                    if player.health <= 0:
                        space.remove(player)
                        space.remove(player.body)
                        dead = True
                    space.remove(enemy_laser)
                    space.remove(enemy_laser.body)
                    enemy.laser_list.remove(enemy_laser)
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