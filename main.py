import pygame 
import sys
import os
import json

pygame.init()

WIDTH = 1000
HEIGHT = 600 
FPS = 60
TILE_SIZE = 100 
GRID_COLS = WIDTH // TILE_SIZE
GRID_ROWS = HEIGHT // TILE_SIZE

clock = pygame.time.Clock() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Dark night") 


background = pygame.image.load('assets/background_night .png').convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 


def load_map(filename='map_data.json'):
  if os.path.exists(filename):
    with open(filename, 'r') as f:
      data = json.load(f) 
    while len(data) < GRID_ROWS:
      data.append([None] * (len(data[0]) if data else GRID_COLS))
    return data[:GRID_ROWS]
  return [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)] 




class Player(pygame.sprite.Sprite):
  def __init__(self, pos_x, pos_y): 
    super().__init__()
    self.x = pos_x
    self.y = pos_y 
    self.direction = 1
    self.speed = 5 
    
    self.frames = {
      'idle' : [
        pygame.image.load('assets/hero/frame_0.png').convert_alpha(),
      ],
      'run': [
        pygame.image.load('assets/hero/frame_1.png').convert_alpha(),
        pygame.image.load('assets/hero/frame_2.png').convert_alpha(),
      ],
      'attack' : [
        pygame.image.load('assets/hero/frame_3.png').convert_alpha(),
        pygame.image.load('assets/hero/frame_4.png').convert_alpha(),
      ],
      'hurt' : [
        pygame.image.load('assets/hero/frame_5.png').convert_alpha(),
        pygame.image.load('assets/hero/frame_6.png').convert_alpha(),
        pygame.image.load("assets/hero/frame_7.png").convert_alpha(),
      ],
      'death' : [
        pygame.image.load('assets/hero/frame_8.png').convert_alpha(),
        pygame.image.load('assets/hero/frame_9.png').convert_alpha(),
        pygame.image.load('assets/hero/frame_10.png').convert_alpha(),
      ]
      
    }
    
    self.state = 'run' 
    self.frame_index = 0
    self.animation_speed = 0.15 
    self.image = self.frames[self.state][self.frame_index] 
    
    self.rect = self.rect = self.image.get_rect()  
    self.rect.topleft = (self.x,self.y) 
    
    
  
  def animate(self):
    current_state_frames = self.frames[self.state]
    self.frame_index += self.animation_speed 
    
    if self.frame_index >= len(current_state_frames):
      self.frame_index = 0 
    
    active_surface = current_state_frames[int(self.frame_index)] 
    active_surface = pygame.transform.scale(active_surface, (150, 150))
    if self.direction == 1:
      self.image = pygame.transform.flip(active_surface, False, False) 
    elif self.direction == -1:
      self.image = pygame.transform.flip(active_surface, True, False)  
  
  def input(self):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
      self.direction = -1
      self.rect[0] -= self.speed
      
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
      self.direction = 1
      self.rect[0] += self.speed 
  
  def check_boundries(self):
    if self.rect[0] <= 0: 
      self.rect[0] = 0
    elif self.rect[0] >= 850:
      self.rect[0] = 850 
      
  
  def draw(self):
    screen.blit(self.image, self.rect)
  
  def update(self):
    self.draw() 
    self.input()
    self.check_boundries()
    self.animate() 


player = Player(50, 50)

while True:
  clock.tick(FPS) 
  screen.fill('black')
  screen.blit(background, (0,0))
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit() 
      break
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        sys.exit()
        break 
  
  player.update()
  pygame.display.update()

pygame.quit() 
      
