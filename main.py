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
MAX_FALL_SPEED = 20
SOLID_TILES = ['tile_0_0', 'tile_0_1', 'tile_0_2']
FOOT_OFFSET = 45 
STATES = ['idle', 'run', 'attack', 'hurt', 'death'] 

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

def frame_number(filename):
  digits = ''.join(ch for ch in filename if ch.isdigit()) 
  return int(digits) if digits else 0 

class Character(pygame.sprite.Sprite):
  def __init__(self, pos_x, pos_y, character_path):
    super().__init__() 
    self.x = pos_x
    self.y = pos_y 
    self.direction = 1 
    self.speed = 5 
    self.state = 'idle' 
    self.character_path = 'hero' 
    self.frames = self.load_frames()  
    self.frame_index = 0 
    self.animation_speed = 0.15 
    self.image = self.frames['idle'][0] 
    self.rect = pygame.Rect(pos_x, pos_y, 150, 150) 
    self.hitbox = pygame.Rect(0, 0, 50, 90) 
    self.hitbox.midbottom = (self.rect.centerx, self.rect.bottom - FOOT_OFFSET) 
    
    
    self.is_attacking = False 
    self.is_hurt = False 
    self.is_dead = False 
    self.hp = 3 
    
    self.x_vel = 0
    self.y_vel = 0
    self.on_ground = False
    self.hit_wall = False 
    
  
  def load_frames(self):
    animation_dict = {}
    for state in STATES:
      animation_dict[state] = [] 
      path = f'assets/{self.character_path}/{state}' 
      if not os.path.exists(path):
        continue
    file_names = sorted([f for f in os.listdir(path) if f.endswith('.png')], key=frame_number) 
    for file in file_names:
      full_path = os.path.join(path, file) 
      img = pygame.image.load(full_path).convert_alpha() 
      animation_dict[state].append(pygame.transform.scale(img, (150, 150)))
    return animation_dict
    
  def can_act(self):
    return not (self.is_attacking or self.is_hurt or self.is_dead) 
  
  def set_state(self, new_state):
    if new_state != self.state and len(self.frames[new_state]) > 0:
      self.state = new_state
      self.frame_index = 0 
  
  def pick_state(self):
    if self.is_dead:
      return 'death'
    if self.is_hurt:
      return 'hurt'
    if self.is_attacking:
      return 'attack'
    if self.x_vel != 0:
      return 'run'
    return 'idle' 
  
  
  
  def animate(self): 
    current_state_frames = self.image 
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
    

class Player(Character):
  def __init__(self, pos_x, pos_y): 
    super().__init__(pos_x, pos_y)
    
    self.hitbox = pygame.Rect(0, 0, 50, 90)
    self.hitbox.midbottom = self.rect.midbottom
    self.jump_power = -15 
    self.on_ground = False 
    self.character = 'player'
  
     
  def input(self):
    if self.character == 'player':
      keys = pygame.key.get_pressed()
      current_action = 'idle'
      self.x_vel = 0 
      
      if not self.is_attacking:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
          self.direction = -1
          current_action = 'run'
          self.x_vel = -self.speed
          
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
          self.direction = 1
          current_action = 'run'
          self.x_vel = self.speed  
      
      if keys[pygame.K_x]:
        self.is_attacking = True 
        current_action = 'attack'  
      
      if keys[pygame.K_SPACE]:
        self.jump() 
      
    if current_action != self.state:
      self.state = current_action
      self.frame_index = 0 
  
  def jump(self):
    if self.character == 'player':
      if self.on_ground:
        self.y_vel = self.jump_power
        self.on_ground = False 
      
  def check_collision(self, grid_data):
    
    self.rect.x += self.x_vel
    self.hitbox.centerx = self.rect.centerx
    self.hitbox.x += self.x_vel 
    self.check_boundries()
    
    player_col = int(self.hitbox.centerx // TILE_SIZE)
    player_row = int(self.hitbox.centery // TILE_SIZE) 
    max_cols = len(grid_data[0]) if grid_data else GRID_COLS
    
    for r in range(max(0, player_row - 2), min(GRID_ROWS, player_row + 3)):
      for c in range(max(0, player_col - 2), min(max_cols, player_col + 3)):

        if grid_data[r][c] in ['tile_0_0', 'tile_0_1', 'tile_0_2']:
          tile_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE) 
          if self.hitbox.colliderect(tile_rect):
            if self.x_vel > 0:
              self.hitbox.right = tile_rect.left
            elif self.x_vel < 0:
              self.hitbox.left = tile_rect.right 
            self.rect.centerx = self.hitbox.centerx

    self.y_vel += GRAVITY
    if self.y_vel > MAX_FALL_SPEED:
      self.y_vel = MAX_FALL_SPEED
      
    self.rect.y += self.y_vel 
    self.hitbox.y += self.y_vel 
    self.on_ground = False 
    
    player_col = int(self.hitbox.centerx // TILE_SIZE)
    player_row = int(self.hitbox.centery // TILE_SIZE)
    
    for r in range(max(0, player_row - 2), min(GRID_ROWS, player_row + 3)):
      for c in range(max(0, player_col - 2), min(max_cols, player_col + 3)):

        if grid_data[r][c] in ['tile_0_0', 'tile_0_1', 'tile_0_2']:
          tile_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE) 
          if self.hitbox.colliderect(tile_rect): 
            if self.y_vel > 0:
              self.hitbox.bottom = tile_rect.top
              self.y_vel = 0
              self.on_ground = True
            elif self.y_vel < 0:
              self.hitbox.top = tile_rect.bottom
              self.y_vel = 0 
            self.rect.bottom = self.hitbox.bottom + 45 
  
  def check_boundries(self):
    map_width = max((len(row) for row in map_data), default=GRID_COLS) * TILE_SIZE
    max_x = max(0, map_width - self.rect.width)
    if self.rect.x <= 0: 
      self.rect.x = 0 
      self.hitbox.centerx = self.rect.centerx
    elif self.rect.x >= max_x:
      self.rect.x = max_x 
      self.hitbox.centerx = self.rect.centerx
      
  def draw(self):
    screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))
  
  def update(self, grid_data):
    global camera_x
    
    self.input()
    self.check_collision(grid_data)
    
    map_width = max((len(row) for row in map_data), default=GRID_COLS) * TILE_SIZE
    camera_x = max(0, min(self.rect.x - WIDTH // 2, map_width - WIDTH))
    self.animate()
    self.draw()


# class Enemy(pygame.sprite.Sprite):
#   def __init__(self, pos_x, pos_y): 
#     super().__init__(pos_x, pos_y) 
    
#     self.frames = {
#           'idle' : [pygame.image.load('assets/enemy/frame_0.png').convert_alpha()],
#           'run': [
#             pygame.image.load('assets/enemy/frame_1.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_2.png').convert_alpha(),
#           ],
#           'attack' : [
#             pygame.image.load('assets/enemy/frame_3.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_4.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_5.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_6.png').convert_alpha(), 
#           ],
#           'hurt' : [
#             pygame.image.load("assets/enemy/frame_7.png").convert_alpha(),
#           ],
#           'death' : [
#             pygame.image.load('assets/enemy/frame_7.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_8.png').convert_alpha(),
#             pygame.image.load('assets/enemy/frame_9.png').convert_alpha(),
#           ]
#         }
    
#     self.direction = 1  
#     self.speed = 5
#     self.character = 'enemy' 
  
#   def move(self, screen):
#     collision_line = (screen, 'red', self.x, self.x * self.direction + 30)
#     pygame.draw.line(collision_line) 
    
  
  # def update(self, screen):
  #   self.move(screen)  
  
  
  

player = Player(50, 50)
# enemy = Enemy(100, 50) 
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
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        sys.exit()
      if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
        player.jump()
      if event.key == pygame.K_r:
        map_data = load_map() 
  
  player.update(map_data)
  # enemy.update(map_data) 
  pygame.display.update() 

pygame.quit()
