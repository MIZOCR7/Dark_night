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
GRAVITY = 0.75 

clock = pygame.time.Clock() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Dark night") 


background = pygame.image.load('assets/background_night .png').convert_alpha() 
background = pygame.transform.scale(background, (WIDTH, HEIGHT)) 


def load_tile_images():
  tiles_folder = 'assets/tiles'
  tiles = {}
  if os.path.exists(tiles_folder):
    for filename in os.listdir(tiles_folder):
      if filename.endswith('.png'):
        tile_name = os.path.splitext(filename)[0]        
        file_path = os.path.join(tiles_folder, filename)
        img = pygame.image.load(file_path).convert_alpha() 
        tiles[tile_name] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
  return tiles 

def draw_map(screen, grid_data, tile_images, camera_x=0):
  first_col = camera_x // TILE_SIZE
  for row_idx, row in enumerate(grid_data):
    for col_idx in range(first_col, min(first_col + GRID_COLS + 1, len(row))):
      tile_name = row[col_idx] 
      if tile_name in tile_images:
        screen.blit(tile_images[tile_name], (col_idx * TILE_SIZE - camera_x, row_idx * TILE_SIZE))

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
    
    self.state = 'idle' 
    self.frame_index = 0
    self.animation_speed = 0.15 
    self.image = self.frames[self.state][self.frame_index] 
    
    self.rect = self.rect = self.image.get_rect()  
    self.rect.topleft = (self.x,self.y) 
    
    self.is_attacking = False 
    self.y_vel = 0
    self.jump_power = 16 
    
    self.on_ground = True 
    
  
  def animate(self):
    current_state_frames = self.frames[self.state]
    self.frame_index += self.animation_speed 
    
    if self.frame_index >= len(current_state_frames):
      self.is_attacking = False 
      self.frame_index = 0 
      
    
    active_surface = current_state_frames[int(self.frame_index)] 
    active_surface = pygame.transform.scale(active_surface, (150, 150))
    if self.direction == 1:
      self.image = pygame.transform.flip(active_surface, False, False) 
    elif self.direction == -1:
      self.image = pygame.transform.flip(active_surface, True, False) 
     
  
  def input(self):
    keys = pygame.key.get_pressed()
    
    current_action = 'idle'
    if not self.is_attacking:
      if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        self.direction = -1
        current_action = 'run'
        self.rect[0] -= self.speed
        
      if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        self.direction = 1
        current_action = 'run'
        self.rect[0] += self.speed  
    
    if keys[pygame.K_x]:
      self.is_attacking = True 
      self.attack = True
      current_action = 'attack'  
    
    if keys[pygame.K_SPACE]:
      self.on_ground = False 
      self.rect[1] -= self.jump_power
      
    if current_action != self.state:
      self.state = current_action
      self.frame_index = 0 
  
  def jump(self):
    if self.on_ground:
      self.y_vel = self.jump_power
      self.on_ground = False 
      
  
  
  def check_boundries(self):
    map_width = max((len(row) for row in map_data), default=GRID_COLS) * TILE_SIZE
    max_x = max(0, map_width - self.rect.width)
    if self.rect[0] <= 0: 
      self.rect[0] = 0
    elif self.rect[0] >= max_x:
      self.rect[0] = max_x 
      
  
  def draw(self):
    screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))
  
  def update(self):
    global camera_x
    
    # self.y_vel -= GRAVITY 
    # self.rect[1] -= self.y_vel 
    
    self.input()
    self.check_boundries() 
    map_width = max((len(row) for row in map_data), default=GRID_COLS) * TILE_SIZE
    camera_x = max(0, min(self.rect.x - WIDTH // 2, map_width - WIDTH))
    self.animate()
    self.draw()


player = Player(50, 50)
map_data = load_map()
tile_images = load_tile_images()
camera_x = 0

while True:
  clock.tick(FPS) 
  screen.fill('black')
  screen.blit(background, (0,0))
  
  draw_map(screen, map_data, tile_images, camera_x)
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      sys.exit() 
      break
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        sys.exit()
      if event.key == pygame.K_r:
        map_data = load_map() 
        break 
  
  player.update()
  pygame.display.update()

pygame.quit() 
      
