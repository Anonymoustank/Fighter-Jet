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
WHITE = (255, 255, 255)
options = DrawOptions()
destination = 0, 0
WIDTH, HEIGHT = 1920, 1080
window = pyglet.window.Window(WIDTH, HEIGHT, "Game", resizable = True)
window.set_fullscreen(True) 
space = pymunk.Space()
health_bar_list = []
speed = 650

class Laser(pymunk.Segment):
    def __init__(self, position, angle, color = GREEN):
        super().__init__(pymunk.Body(1, 100), (0, 0), (20, 0), 3)
        self.color = color
        self.sensor = True
        self.body.position = position
        self.body.angle = angle
        self.body.velocity = Vec2d(math.cos(self.body.angle), math.sin(self.body.angle)) * 800
        self.damage = 12.5

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
        self.time_since_variance = time.perf_counter() - 0.2 #only for enemies
        self.x, self.y = self.position
        self.health_bar_length = 30
        self.health_bar = pyglet.shapes.Rectangle(self.x - 20, self.y - 75, self.health_bar_length, 5, RED)
        self.total_health = pyglet.shapes.Rectangle(self.x - 20, self.y - 75, self.health_bar_length * (self.health/100), 5, GREEN)
        self.blitz = False
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
            if abs(self.cooldown - time.perf_counter()) >= (1/4):
                self.cooldown = time.perf_counter()
                variance = random.uniform(-1 * math.pi/25, math.pi/25)
                self.laser_list.append(Laser(self.body.position, self.body.angle + variance))
                self.laser_list[len(self.laser_list) - 1].damage = 25
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)
        elif self.laser_type == "sniper":
            if abs(self.cooldown - time.perf_counter()) >= (1):
                self.cooldown = time.perf_counter()
                self.laser_list.append(Laser(self.body.position, self.body.angle, WHITE))
                self.laser_list[len(self.laser_list) - 1].body.velocity = self.laser_list[len(self.laser_list) - 1].body.velocity * 4
                self.laser_list[len(self.laser_list) - 1].damage = 50
                space.add(self.laser_list[len(self.laser_list) - 1])
                space.add(self.laser_list[len(self.laser_list) - 1].body)
        elif self.laser_type == "blitz":
            if abs(self.cooldown - time.perf_counter()) >= (1.5):
                self.cooldown = time.perf_counter()
                self.blitz = True
                

player = Ship(GREEN, "default")
enemy_list = []
for i in range(1):
    enemy_list.append(Ship(RED, "default"))
    space.add(enemy_list[len(enemy_list) - 1])
    space.add(enemy_list[len(enemy_list) - 1].body)
    enemy_list[len(enemy_list) - 1].body.position = WIDTH // 2, HEIGHT // 2
started = False
dead = False

wall1_body = pymunk.Body(1, 100, pymunk.Body.KINEMATIC)
wall1_body.position = WIDTH + 5, HEIGHT // 2
right_wall = pymunk.Poly.create_box(wall1_body, size = (10, HEIGHT))
wall1_body.elasticity, right_wall.elasticity = 0, 0

wall2_body = pymunk.Body(1, 100, pymunk.Body.KINEMATIC)
wall2_body.position = 0 - 5, HEIGHT // 2
left_wall = pymunk.Poly.create_box(wall2_body, size = (10, HEIGHT))
wall2_body.elasticity, left_wall.elasticity = 0, 0

wall3_body = pymunk.Body(1, 100, pymunk.Body.KINEMATIC)
wall3_body.position = WIDTH // 2, HEIGHT + 5
top_wall = pymunk.Poly.create_box(wall3_body, size = (WIDTH, 10))
wall3_body.elasticity, top_wall.elasticity = 0, 0

wall4_body = pymunk.Body(1, 100, pymunk.Body.KINEMATIC)
wall4_body.position = WIDTH // 2, 0 - 5
bottom_wall = pymunk.Poly.create_box(wall4_body, size = (WIDTH, 10))
wall4_body.elasticity, bottom_wall.elasticity = 0, 0

space.add(player, player.body, wall1_body, wall2_body, wall3_body, wall4_body, right_wall, left_wall, top_wall, bottom_wall)
space.gravity = 0, 0

is_held_down = False

@window.event
def on_mouse_press(x, y, button, modifiers):
    global started
    started = True

@window.event
def on_key_press(symbol, modifiers):
    if symbol == key.SPACE:
        global is_held_down
        is_held_down = True
    if symbol == key.ENTER:
        global started
        started = True

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
    if started == True and dead == False:
        space.debug_draw(options)
        if dead == False:
            player_x, player_y = player.body.position
            player.health_bar.position = player_x - 20, player_y - 75
            player.health_bar.draw()
            player.total_health = pyglet.shapes.Rectangle(player_x - 20, player_y - 75, player.health_bar_length * (player.health/100), 5, GREEN)
            player.total_health.draw()
            for i in enemy_list:
                i_x, i_y = i.body.position
                i.health_bar.position = i_x - 20, i_y - 75
                i.health_bar.draw()
                i.total_health = pyglet.shapes.Rectangle(i_x - 20, i_y - 75, i.health_bar_length * (i.health/100), 5, GREEN)
                i.total_health.draw()
    elif started == False:
        label = pyglet.text.Label('Press Enter/Return to Start', font_name='Comic Sans', font_size=24, x=window.width/2, y=window.height/2, anchor_x='center', anchor_y='center')
        label.draw()
    elif dead == True:
        death_label = pyglet.text.Label('Game Over', font_name='Comic Sans', font_size=24, x=window.width/2, y=window.height/2, anchor_x='center', anchor_y='center')
        death_label.draw()

def refresh(dt):
    global dead
    if is_held_down == True and dead == False and started == True:
        player.shoot()
    if dead == False and started == True:
        if player.blitz == True:
            global speed
            if abs(player.cooldown - time.perf_counter()) <= (1/4):
                speed = 1625
            else:
                player.cooldown = time.perf_counter()
                speed = 650
                player.blitz = False
        else:
            speed = 650
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

    if dead == False and len(enemy_list) > 0 and started == True:
        for i in enemy_list:
            i.shoot()
            body_x, body_y = i.body.position
            x, y = player.body.position
            if abs(time.perf_counter() - i.time_since_variance) >= (0.15):
                variance_num = random.uniform(-1 * math.pi/20, math.pi/20)    
                global desired_angle
                desired_angle = math.atan2(body_y - y, body_x - x) - (math.pi) + variance_num
                i.time_since_variance = time.perf_counter()
            rotation_angle = math.pi/16
            if player.body.velocity == (0, 0):
                i.body.angle = 0.0
                desired_angle = i.body.angle + math.atan2(body_y - y, body_x - x) - (math.pi)
                i.body.angle = desired_angle
            elif abs(desired_angle - i.body.angle) < rotation_angle:
                while i.body.angle >= 2 * math.pi:
                    i.body.angle = i.body.angle / 2 * math.pi
                while i.body.angle <= -2 * math.pi:
                    i.body.angle = i.body.angle / -2 * math.pi
                i.body.angle = desired_angle
            elif desired_angle < 0:
                i.body.angle -= rotation_angle
                while i.body.angle <= -2 * math.pi:
                    i.body.angle = i.body.angle / (-2 * math.pi)
            elif desired_angle >= 0:
                i.body.angle += rotation_angle
                while i.body.angle >= 2 * math.pi:
                    i.body.angle = i.body.angle / 2 * math.pi
            else:
                while i.body.angle >= 2 * math.pi:
                    i.body.angle = i.body.angle / 2 * math.pi
                while i.body.angle <= -2 * math.pi:
                    i.body.angle = i.body.angle / -2 * math.pi

            distance = math.sqrt((x - body_x) ** 2 + (y - body_y) ** 2)
            if distance >= 200:
                i.body.velocity = Vec2d(math.cos(i.body.angle), math.sin(i.body.angle)) * 400
            else:
                i.body.velocity = 0, 0

    if dead == False and started == True:
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
        if player.blitz == False:
            body_x, body_y = player.body.position
            x, y = destination
            player.body.angle = 0.0
            player.body.angle = player.body.angle + math.atan2(body_y - y, body_x - x) - (math.pi)
            distance = math.sqrt((x - body_x) ** 2 + (y - body_y) ** 2)
        if distance >= 10 or player.blitz == True:
            if player.blitz == True:
                global continue_forward
                continue_forward = True
                for i in [right_wall, left_wall, top_wall, bottom_wall]:
                    if len(i.shapes_collide(player).points) != 0:
                        continue_forward = False
                if continue_forward == True:
                    player.body.velocity = Vec2d(math.cos(player.body.angle), math.sin(player.body.angle)) * speed
                else:
                    player.body.velocity = 0, 0
                    player.blitz = False
            else:
                player.body.velocity = Vec2d(math.cos(player.body.angle), math.sin(player.body.angle)) * speed
        else:
            player.body.velocity = 0, 0
    space.step(dt)

if __name__ == "__main__":
    pyglet.clock.schedule_interval(refresh, 1.0/120.0)
    pyglet.app.run()