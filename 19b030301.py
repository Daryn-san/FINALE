import pygame
import random
import time
import pika
import json
from threading import Thread
from enum import Enum
import uuid
from pygame import mixer

pygame.init()

IP = '34.254.177.17'
PORT = '5672'
VIRTUAL_HOST = 'dar-tanks'
USERNAME = 'dar-tanks'
PASSWORD = '5orPLExUYnyVYZg48caMpX'

class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

width = 800
height = 600
screen = pygame.display.set_mode((width, height))
boosterIMG=pygame.image.load('img/powerup.png')
wallImage=pygame.image.load('img/brick.png')
mixer.music.load('soundeffects/megalovania.mp3')
mixer.music.play(-1)
shotSound =pygame.mixer.Sound('soundeffects/shot.wav')
explosionSound =pygame.mixer.Sound('soundeffects/explosion.wav')
font = pygame.font.SysFont('Courier New', 40)
bont = pygame.font.SysFont('Courier New', 29)

#duel

class Tank:
    def __init__(self, tank_id, x, y, speed, color, d_right, d_left, d_up, d_down, d_pull):
        self.id = tank_id
        self.x = x
        self.y = y
        self.life = 3
        self.speed = 3
        self.color = color
        self.width = 31
        self.direction = Direction.RIGHT

        self.KEY = {d_right: Direction.RIGHT, d_left: Direction.LEFT,
                    d_up: Direction.UP, d_down: Direction.DOWN}
        self.KEYPULL=d_pull
    def draw(self):
        tank_c = (self.x + int(self.width / 2), self.y + int(self.width / 2))
        pygame.draw.rect(screen, self.color, 
                         (self.x, self.y, self.width, self.width), 8)
        pygame.draw.circle(screen, self.color, tank_c, int(self.width / 3))

        if self.direction == Direction.RIGHT:
            pygame.draw.line(screen, self.color, tank_c, (self.x + self.width + int(self.width / 2), self.y + int(self.width / 2)), 4)
        if self.direction == Direction.LEFT:
            pygame.draw.line(screen, self.color, tank_c, (
            self.x - int(self.width / 2), self.y + int(self.width / 2)), 4)
        if self.direction == Direction.UP:
            pygame.draw.line(screen, self.color, tank_c, (self.x + int(self.width / 2), self.y - int(self.width / 2)), 4)
        if self.direction == Direction.DOWN:
            pygame.draw.line(screen, self.color, tank_c, (self.x + int(self.width / 2), self.y + self.width + int(self.width / 2)), 4)

    def change_direction(self, direction):
        self.direction = direction
    
    def move(self):
        if self.direction == Direction.LEFT:
            self.x -= self.speed
        if self.direction == Direction.RIGHT:
            self.x += self.speed
        if self.direction == Direction.UP:
            self.y -= self.speed
        if self.direction == Direction.DOWN:
            self.y += self.speed
        
        if self.y <0:
            self.y = height
        if self.y > height:
            self.y = 0
        if self.x < 0:
            self.x = width
        if self.x > width:
            self.x = 0
        self.draw()

FPS = 50
clock = pygame.time.Clock()

class Shot:
    def __init__(self,x=0,y=0,color=(0,0,0),direction=Direction.LEFT,speed=12):
        self.x=x
        self.y=y
        self.color=color
        self.speed=speed
        self.direction=direction
        self.status=True
        self.distance=0
        self.radius=5
    
    def move(self):
        if self.direction == Direction.LEFT:
            self.x -= self.speed
        if self.direction == Direction.RIGHT:
            self.x += self.speed
        if self.direction == Direction.UP:
            self.y -= self.speed
        if self.direction == Direction.DOWN:
            self.y += self.speed
        self.distance+=1
        if self.distance>(2*width):
            self.status=False
        self.draw()

    def draw(self):
        if self.status:
            pygame.draw.circle(screen,self.color,(self.x,self.y),self.radius)

def give_coordinates(tank):
    if tank.direction == Direction.RIGHT:
        x=tank.x + tank.width + int(tank.width / 2)
        y=tank.y + int(tank.width / 2)

    if tank.direction == Direction.LEFT:
        x=tank.x - int(tank.width / 2)
        y=tank.y + int(tank.width / 2)

    if tank.direction == Direction.UP:
        x=tank.x + int(tank.width / 2)
        y=tank.y - int(tank.width / 2)

    if tank.direction == Direction.DOWN:
        x=tank.x + int(tank.width / 2)
        y=tank.y + tank.width + int(tank.width / 2)

    p=Shot(x,y,tank.color,tank.direction)
    shot.append(p)

class Booster:
    def __init__(self):
        self.x = random.randint(100,800)
        self.y = random.randint(100,600)
        self.radius = 30
        self.status = True
    def draw(self):
        if self.status: 
            screen.blit(boosterIMG ,(self.x, self.y))

class Wall:
    def __init__(self):
        self.x = random.randint(100,800)
        self.y = random.randint(100,600)
        self.width = 10
        self.height = 10
        self.status = True

    def draw(self):
        if self.status:
            screen.blit(wallImage,(self.x, self.y))

def collision():
    for p in shot:
        for tank in tanks:
            if (tank.x+tank.width+p.radius > p.x > tank.x - p.radius ) and ((tank.y+tank.width + p.radius > p.y > tank.y - p.radius)) and p.status==True:
                explosionSound.play()
                p.color=(0,0,0)
                tank.life -=1
                p.status=False
                
                tank.x=random.randint(50,width-70)
                tank.y=random.randint(50,height-70)

def life():
    life1=tanks[1].life
    life2=tanks[0].life
    res = bont.render("1's Player's Life: " + str(life1), True, (255, 123, 100))
    res1 = bont.render("2's Player's Life: " + str(life2), True, (100, 230, 40))
    screen.blit(res, (40,70))
    screen.blit(res1, (420,70))

tank1 = Tank(1, 50, 50, 3, (240, 240, 0), pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_SPACE)
tank2 = Tank(2, 700, 500 ,3, (200, 0, 200), pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN)

map= [Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall(),Wall()]
tanks = [tank1, tank2]
shot = []
booster0 = Booster()
boosters = [booster0]

def mainpage():
    wallpaper = pygame.image.load('img/wallpaper.png')
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Choose Your Hero!")
    screen.blit(wallpaper, (0, 0))
    screen.blit(font.render("press Enter to play duel ", 1, (255,255,255)), font.render("press Enter to play duel ", 1, (0,0,0)).get_rect(center = (420,200)))
    screen.blit(font.render("press Space to play multiplayer ", 1, (255,255,255)), font.render("press Space to play 1 vs server players ", 1, (0,0,0)).get_rect(center = (500,300)))
    screen.blit(font.render("press Ctrl to play AI mode", 1, (255,255,255)), font.render("press Ctrl to watch AI mode ", 1, (0,0,0)).get_rect(center = (450,400)))
    screen.blit(font.render("press Esc to quit", 1, (255,255,255)), font.render("press Esc to watch quit ", 1, (0,0,0)).get_rect(center = (470,500)))
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                quit()   
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                duel()
            if event.key == pygame.K_SPACE:
                multiplayer()
            if event.key == pygame.K_LCTRL:
                AImode()

def duel():
    start_time = None
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Courier New', 40)
    mainloop = True
    lifely = True
    time1 = 0
    time2 = 0
    timer1 = False
    timer2 = False
    while mainloop:
        mills = clock.tick(FPS)
        if lifely:
            start_time = pygame.time.get_ticks()
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("DUEL")
        screen.fill((127,255,212))
        background = pygame.Surface((200,700))
        screen.blit(background,(800,0))
        life()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                pressed = pygame.key.get_pressed()
                start_time = pygame.time.get_ticks()
                for tank in tanks:
                    if event.key in tank.KEY.keys():
                        tank.change_direction(tank.KEY[event.key])
                    if event.key in tank.KEY.keys():
                        tank.move()
                    if pressed[tank.KEYPULL]:
                        shotSound.play()
                        give_coordinates(tank)

                
        for p in shot:
            for tank in tanks:
                if (tank.x+tank.width+p.radius > p.x > tank.x - p.radius ) and ((tank.y+tank.width + p.radius > p.y > tank.y - p.radius)) and p.status==True:
                    explosionSound.play()
                    p.color=(0,0,0)
                    tank.life -= 1
                    p.status=False
                    tank.x=random.randint(50,width-50)
                    tank.y=random.randint(50,height-50)
                if tank.life == 0:
                    font = pygame.font.SysFont("Times New Roman", 70)     
                    text = font.render("GG WP", 1, (0,0,0)) 
                    place = text.get_rect(center = (400,100))   
                    screen.blit(text, place) 
                    tank1.speed = 0
                    tank2.speed = 0
                    lifely = False
        
        if start_time:
            time_since_enter = ((pygame.time.get_ticks() + start_time)/1000)
        message = 'Seconds since enter: ' + str(time_since_enter)
        screen.blit(font.render(message, True, (255,255,255)), (20, 20))
        
        
        for wall in map:
            for tank in tanks:
                if (wall.x + wall.height > tank.x + 9 > wall.x - tank.width) and (wall.y + wall.width> tank.y + 9> wall.y) and wall.status==True:
                    explosionSound.play()
                    wall.color=(0,0,0)
                    tank.life -= 1
                    wall.status=False
                if tank.life == 0:
                    font = pygame.font.SysFont("Times New Roman", 70)     
                    text = font.render("GG WP", 1, (0,0,0)) 
                    place = text.get_rect(center = (400,60))   
                    screen.blit(text, place) 
                    tank1.speed = 0
                    tank2.speed = 0
                    lifely = False



        for p in shot:
            for wall in map:
                if (wall.x + wall.height> p.x > wall.x ) and (wall.y + wall.width> p.y > wall.y) and p.status==True and wall.status == True:
                    explosionSound.play()
                    p.color=(0,0,0)
                    p.status=False
                    wall.status = False

        if (booster0.x + booster0.radius > tank1.x + 9 > booster0.x ) and (booster0.y + booster0.radius> tank1.y + 9 > booster0.y) and booster0.status == True:
            booster0.status = False
            timer1 = True
        if (booster0.x + booster0.radius > tank2.x + 9 > booster0.x ) and (booster0.y + booster0.radius> tank2.y + 9 >booster0.y) and booster0.status == True:
            booster0.status = False
            timer2 = True
            if timer1:
                time1 = time1 + (mills / 1000)
        if timer2:
            time2 = time2 + (mills / 1000)
        if time1 < 5 and time1 != 0:
            if lifely:
                tank1.speed = 4
                l0 = 5 - time1
                scor = "%.2f" % l0  
                text = font.render(scor, 1, (0, 191,255))   
                screen.blit(text, (930,500)) 
        elif time2 < 5 and time2 != 0:
            if lifely:
                tank2.speed = 4
                l0 = 5 - time2
                scor = "%.2f" % l0    
                text = font.render(scor, 1, (255, 0, 0))    
                screen.blit(text, (930,290))
        else:
            if lifely:
                tank1.speed = 2
                tank2.speed = 2
            booster0.status = True
            timer1 = False
            time1 = 0
            timer2 = False
            time2 = 0
                    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    mainloop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        mainloop = False
         
        for p in shot:
            p.move()
        for tank in tanks:
            tank.draw()
            tank.move()
        for wall in map:
            wall.draw()
        for booster in boosters:
            booster.draw() 

        pygame.display.flip()

#multiplayer
class TankRPCproducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host = IP,
                port = PORT,
                virtual_host = VIRTUAL_HOST,
                credentials = pika.PlainCredentials(
                    username = USERNAME,
                    password = PASSWORD
               )
            )
        )
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue = '', auto_delete = True, exclusive = True)
        self.queue_callback = result.method.queue

        self.channel.queue_bind(exchange = 'X:routing.topic',
                                queue = self.queue_callback)

        self.channel.basic_consume(
            queue = self.queue_callback,
            on_message_callback = self.callback,
            auto_ack = True
        )
        self.response = None
        self.corr_id = None
        self.token = None
        self.tankid = None
        self.roomid = None
        
    def call(self, rout_key, message = {}):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange = 'X:routing.topic',
            routing_key = rout_key,
            properties = pika.BasicProperties(
                reply_to = self.queue_callback,
                correlation_id = self.corr_id,
            ),
            body=json.dumps(message)
        ) 
        while self.response is None:
            self.connection.process_data_events()

    def callback(self, ch, method, properties, body):
        if self.corr_id == properties.correlation_id:
            self.response = json.loads(body)
            print(self.response)

    def health_check(self):
        self.call('tank.request.healthcheck')
        if self.response['status'] == '200':
            return True
        return False

    def register(self, room_id):
        message = {
            'roomId': room_id
        }
        self.call('tank.request.register', message)
        if 'token' in self.response:
            self.token = self.response['token']
            self.tankid = self.response['tankId']
            
            return True
        return False
    
    def turn_tank(self, token, direction):
        message = {
            'token': token,
            'direction': direction
        }
        self.call('tank.request.turn', message)

    def fire_bullet(self, token):
        message = {
            'token': token
        }
        self.call('tank.request.fire', message)
    
class TankConsumerClient(Thread):
    def __init__(self, room_id):
        super().__init__()
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host = IP,
                port = PORT,
                virtual_host = VIRTUAL_HOST,
                credentials = pika.PlainCredentials(
                    username = USERNAME,
                    password = PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()
        queue=self.channel.queue_declare(queue = '',
                                        auto_delete = True,
                                        exclusive = True
                                        )
        event_listener = queue.method.queue
        self.channel.queue_bind(exchange='X:routing.topic',
        queue=event_listener,
        routing_key='event.state.'+room_id
        )
        self.channel.basic_consume(
            queue=event_listener,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        self.response = None
    def on_response(self, ch, method, props, body):
        self.response = json.loads(body)
    def run(self):
        self.channel.start_consuming()

class player_loser():
    def __init__(self):
        self.state_case = False 
        self.state = False
        self.score = 0
    def loser_display(self):
        def blit_loser():
            pygame.display.set_mode((1100, 600))
            screen.blit((0,0,0))
            blittext("You lose", 550,180, 40, (255,223,0))
            blittext("To Replay, press [R]", 550, 280, 30, (255,0,0))
            blittext('Your Score: ' + str(self.score), 550, 380, 40, (255,0,0))
        running_loser = True
        while running_loser:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_loser = False
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_loser = False
                        pygame.quit()
                    if event.key == pygame.K_r:
                        running_loser = False 
                        mainloop()
                        self.state = False
            blit_loser()
            pygame.display.flip()

class player_winner():
    def __init__(self):
        self.state = False 
        self.score = 0
    def winner_display(self):
        def blit_winner():
            pygame.display.set_mode((1100, 600))
            screen.fill((34, 77, 23))    
            blittext("You win!", 550,180, 40, (255,223,0))
            blittext("To play again, press [R]", 550, 280, 30, (255,0,0))
            blittext('Your Score: ' + str(self.score), 550, 380, 30, (255,0,0))
        running_winner = True
        while running_winner:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running_winner = False
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running_winner = False 
                        pygame.quit()
                    if event.key == pygame.K_r:
                        running_winner = False 
                        mainloop()
                        self.state = False 
            
            blit_winner()
            pygame.display.flip()

class player_kicked():
    def __init__(self):
        self.score = 0
        self.state = False 
    def kicked_display(self): 
        def blit_kicked():
            pygame.display.set_mode((1100, 600))
            screen.fill((0,0,0))
            blittext('You were kicked', 550,180, 40, (240,255,240))
            blittext("to Replay, press [R]", 550, 280, 30, (240,255,240))
            blittext('Your Score: ' + str(self.score), 550, 380, 30, (240,255,240))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False 
                        pygame.quit()
                    if event.key == pygame.K_r:
                        running = False 
                        mainloop()
                        self.state = False 
            blit_kicked()
            pygame.display.flip()

UP = 'UP'
DOWN = 'DOWN'
RIGHT = 'RIGHT'
LEFT = 'LEFT'

MOVE_KEYS = {
    pygame.K_w: UP,
    pygame.K_a: LEFT,
    pygame.K_d: RIGHT,
    pygame.K_s: DOWN
    }

def draw_tanks(x, y, width, height, direction, color_tank):
    tank_center = (x + width // 2, y + height // 2)        

    pygame.draw.rect(screen, color_tank, (x, y, width, height), 6)
    pygame.draw.circle(screen, color_tank, tank_center, width // 2,4)
    if direction == 'RIGHT':
        pygame.draw.line(screen, color_tank, (tank_center[0] + width // 2,tank_center[1]), (x + width + width // 2, y + height // 2), 4)
    if direction == 'LEFT':
        pygame.draw.line(screen, color_tank, (tank_center[0] - width // 2,tank_center[1]), (x - width // 2, y + height // 2), 4)
    if direction == 'UP':
        pygame.draw.line(screen, color_tank, (tank_center[0],tank_center[1] - width // 2), (x + width // 2, y - height // 2), 4)
    if direction == 'DOWN':
        pygame.draw.line(screen, color_tank, (tank_center[0],tank_center[1] + width // 2), (x + width // 2, y + height + height // 2), 4)

def blittext(text, x, y, size, color):
    font =pygame.font.SysFont('Times new roman', size)
    ttext = font.render(text, True, color)
    ttextRect = ttext.get_rect()
    ttextRect.center = (x, y)    
    screen.blit(ttext, ttextRect)

def draw_bullets(x, y, width, height, color_bullet):
    pygame.draw.rect(screen, color_bullet,(x, y, width, height))

def multiplayer():
    mainloop = True
    screen = pygame.display.set_mode((1000,600))
    r = TankRPCproducer()
    r.health_check()
    r.register('room-15')
    event_collect = TankConsumerClient('room-15')
    event_collect.start()
    kick = player_kicked()
    winner = player_winner()
    loser = player_loser()
    pygame.display.set_caption("Multiplayer")
    while mainloop:
        pygame.display.set_caption("Multiplayer")
        screen.fill((127,255,212))
        pygame.draw.rect(screen, (51,21,0), (800, 0, 1000, 600))
        tanks = event_collect.response['gameField']['tanks']
        rem_time = event_collect.response['remainingTime']
        bullets = event_collect.response['gameField']['bullets']
        losers = event_collect.response['losers']
        winners = event_collect.response['winners']
        kicked = event_collect.response['kicked']
        if rem_time == 1:
            for member in winners:
                if r.tankid == member['tankId']:
                    mainloop = False 
                    winner.state = True
                    winner.score = member['score']
            for member in losers:
                if r.tankid == member['tankId']:
                    mainloop = False 
                    loser.state = True 
                    loser.score = member['score']
        blittext("Boss", 900, 10, 20, (0, 191,255))
        blittext("You          Health      Score", 900, 50, 16, (0, 191,255))
        blittext("Opponents", 900, 120, 20, (255,0,0))
        blittext("Enemies    Health   Score", 900, 140, 16, (255,0,0))
        blittext("Time remained: {}".format(rem_time), 850, 580, 18, (221, 160, 221))
        l = len(tanks) - 1
        f = l
        c_tanks = 0
        t = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                if event.key in MOVE_KEYS:
                    r.turn_tank(r.token, MOVE_KEYS[event.key])
                if event.key == pygame.K_SPACE:
                    r.fire_bullet(r.token)

        for member in kicked:
            if r.tankid == member['tankId']: 
                kick.state = True 
                kick.score = member['score']
                mainloop = False
        for member in losers:
            if r.tankid == member['tankId']:
                loser.state = True 
                loser.score = member['score']
                mainloop = False
        for member in winners:
            if r.tankid == member['tankId']: 
                winner.state = True
                winner.score = member['score']
                mainloop = False
        try:
            for tank in tanks:
                if r.tankid == tank['id']:
                    draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], (0, 191,255))
                else:
                    c_tanks += 1
                    draw_tanks(tank['x'], tank['y'], tank['width'],tank['height'], tank['direction'], (255,0,0))
        except:
            pass
        try:
            for bullet in bullets:
                if r.tankid == bullet['owner']:
                    draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], (0, 191,255))
                else:
                    draw_bullets(bullet['x'], bullet['y'], bullet['width'], bullet['height'], (255,0,0))
        except:
            pass        
        try:
            for tank in tanks:
                if r.tankid == tank['id']:                
                    blittext(tank['id'] + "       " + str(tank['health']) + "            " + str(tank['score']), 900,70,17, (0, 191,255))
                else:
                    blittext(tank['id'] + "       " + str(tank['health']) + "            " + str(tank['score']), 900,160 + (20 * t),17, (255,0,0))
                    t = t + 1
                    if f == 0:
                        t = 0
                        f = g
                    f = f - 1
                if c_tanks + 1 != len(tanks):
                    mainloop = False
                    loser.state_case = True
        except:
            pass
        pygame.display.flip()
                
    if kick.state == True:
        kick.kicked_display()
    elif winner.state == True:
        winner.winner_display()
    elif loser.state == True:
        loser.loser_display()
    elif loser.state_case == True:
        loser.loser_display()

 

while True:
    mainpage()

pygame.quit()