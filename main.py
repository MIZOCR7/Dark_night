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
STATES = ['idle', 'run', 'attack', 'hurt', 'death', 'chase', 'patrol'] 

clock = pygame.time.Clock() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Dark night") 

background_path = os.path.join("assets", "background_night.png")

if not os.path.exists(background_path):
    raise FileNotFoundError(
        f"Background image not found: {background_path}"
    )

background = pygame.image.load(background_path).convert_alpha()
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

def load_map(filename="map_data.json"):
    if not os.path.exists(filename):
        return [
            [None for _ in range(GRID_COLS)]
            for _ in range(GRID_ROWS)
        ]

    with open(filename, "r") as f:
        data = json.load(f)

    if not data:
        data = []

    map_cols = max([GRID_COLS] + [len(row) for row in data if isinstance(row, list)])

    normalized_data = []

    for row in data:

        normalized_row = list(row)  

        while len(normalized_row) < map_cols:  
            normalized_row.append(None)

        normalized_data.append(normalized_row)

    
    while len(normalized_data) < GRID_ROWS:
        normalized_data.append([None] * map_cols)  

    return normalized_data[:GRID_ROWS]  

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
    self.character_path = character_path 
    self.frames = self.load_frames()  
    self.frame_index = 0 
    self.animation_speed = 0.15 
    
    self.faces_right = True
    self.rect = pygame.Rect(pos_x, pos_y, 150, 150) 
    self.hitbox = pygame.Rect(0, 0, 50, 90) 
    self.hitbox.midbottom = (self.rect.centerx, self.rect.bottom - FOOT_OFFSET) 
    
    if self.frames.get('idle') and len(self.frames['idle']) > 0:
      self.image = self.frames['idle'][0] 
    else:
      self.image = pygame.Surface((50, 50))
      self.image.fill((255, 0, 0))
    
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
  
  def take_hit(self):
    if self.is_dead or self.is_hurt:
      return
    self.hp -= 1
    self.is_attacking = False
    if self.hp <= 0:
      self.is_dead = True
      self.set_state('death')
    elif len(self.frames['hurt']) > 0:
      self.is_hurt = True
      self.set_state('hurt') 
  
  def animate(self):
    current_state_frames = self.frames.get(self.state, [])

    
    if not current_state_frames:
        idle_frames = self.frames.get("idle", [])

        self.state = "idle"
        self.frame_index = 0
        current_state_frames = idle_frames

    if not current_state_frames: 
        return

    self.frame_index += self.animation_speed

    if self.frame_index >= len(current_state_frames):
        if self.state == "death":
            self.frame_index = len(current_state_frames) - 1
        else:
            finished_state = self.state
            self.frame_index = 0

            if finished_state == "attack":
                self.is_attacking = False
            elif finished_state == "hurt":
                self.is_hurt = False

            if finished_state in ("attack", "hurt"):
                self.state = "idle"
                current_state_frames = self.frames.get("idle", [])

                if not current_state_frames:
                    return

    frame_index = min(
        int(self.frame_index),
        len(current_state_frames) - 1
    )

    active_surface = current_state_frames[frame_index]

    if (self.direction == 1) != self.faces_right:
        self.image = pygame.transform.flip(
            active_surface, True, False
        )
    else:
        self.image = active_surface
      
  def check_collision(self, grid_data): 
    self.hit_wall = False 
    self.rect.x += self.x_vel 
    self.hitbox.centerx = self.rect.centerx 
    self.check_boundaries(grid_data)
    
    player_col = int(self.hitbox.centerx // TILE_SIZE) 
    player_row = int(self.hitbox.centery // TILE_SIZE) 
    max_cols = len(grid_data[0]) if grid_data else GRID_COLS 
    
    for r in range(max(0, player_row - 2), min(GRID_ROWS, player_row + 3)):
      for c in range(max(0, player_col - 2), min(max_cols, player_col + 3)):
        
        if grid_data[r][c] in SOLID_TILES:
          tile_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE) 
          if self.hitbox.colliderect(tile_rect):
            if self.x_vel > 0:
              self.hitbox.right = tile_rect.left
            elif self.x_vel < 0:
              self.hitbox.left = tile_rect.right
            self.hit_wall = True 
            self.rect.centerx = self.hitbox.centerx 
    
    self.y_vel += GRAVITY 
    if self.y_vel > MAX_FALL_SPEED:
      self.y_vel = MAX_FALL_SPEED 
      
    self.rect.y += round(self.y_vel) 
    self.hitbox.y += round(self.y_vel) 
    self.on_ground = False 
    
    player_col = int(self.hitbox.centerx // TILE_SIZE) 
    player_row = int(self.hitbox.centery // TILE_SIZE) 
    
    for r in range(max(0, player_row - 2), min(GRID_ROWS, player_row + 3)):
      for c in range(max(0, player_col - 2), min(max_cols, player_col + 3)):

        if grid_data[r][c] in SOLID_TILES:
          tile_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE) 
          if self.hitbox.colliderect(tile_rect):
            if self.y_vel > 0:
              self.hitbox.bottom = tile_rect.top  
              self.y_vel = 0 
              self.on_ground = True 
            elif self.y_vel < 0:
              self.hitbox.top = tile_rect.bottom 
              self.y_vel = 0
            self.rect.bottom = self.hitbox.bottom + FOOT_OFFSET 
  
  def check_boundaries(self, grid_data):
    map_width = max((len(row) for row in grid_data), default=GRID_COLS) * TILE_SIZE
    max_x = max(0, map_width - self.rect.width) 
    if self.rect.x <= 0:
      self.rect.x = 0 
      self.hitbox.centerx = self.rect.centerx 
      self.hit_wall = True 
    elif self.rect.x >= max_x: 
      self.rect.x = max_x 
      self.hitbox.centerx = self.rect.centerx
      self.hit_wall = True 
    
  def draw(self, camera_x):
    screen.blit(self.image, (self.rect.x - camera_x, self.rect.y))     

class Player(Character):
  def __init__(self, pos_x, pos_y): 
    super().__init__(pos_x, pos_y, 'hero') 
    
    self.jump_power = -15 
    self.character = 'player'
    
    
  
     
  def input(self):
    keys = pygame.key.get_pressed()
    self.x_vel = 0 
    
    if self.can_act():
      if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        self.direction = -1 
        self.x_vel = -self.speed 
        
      if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
        self.direction = 1
        self.x_vel = self.speed  
    
      if keys[pygame.K_x]:  
        self.is_attacking = True 
    
      if keys[pygame.K_SPACE]:  
        self.jump() 
    
    self.set_state(self.pick_state()) 
  
  def jump(self):
    if self.on_ground:
      self.y_vel = self.jump_power
      self.on_ground = False 

  
  def update(self, grid_data):
    global camera_x
    
    self.input()
    self.check_collision(grid_data)
    
    map_width = max((len(row) for row in grid_data), default=GRID_COLS) * TILE_SIZE  
    camera_x = max(0, min(self.rect.x - WIDTH // 2, map_width - WIDTH))
    self.animate()


class Skeleton(Character):
  def __init__(self, pos_x, pos_y):
    super().__init__(pos_x, pos_y, 'enemy') 
    self.faces_right = False 
    self.speed = 2 
    self.direction = -1
    self.character = 'enemy' 
    self.patrol_speed = 2
    self.chase_speed = 6
    self.vision_range = 50
    self.vision_height = 60 
    self.vision_rect = pygame.Rect(0, 0, self.vision_range, self.vision_height) 
    
  
  def ai_move(self, player):
    if self.direction == 1:
      self.vision_rect.left = self.rect.right
    else:
      self.vision_rect.right = self.rect.left 
    
    self.vision_rect.centery = self.rect.centery 
    distance_to_player = abs(player.rect.centerx - self.rect.centerx) 
    
    if distance_to_player < 20 and pygame.sprite.collide_rect(self, player):
      self.state = 'attack'
    elif self.vision_rect.colliderect(player.rect):
      self.state = 'chase'
    else:
      self.state = 'patrol' 
    
    
    if self.state == 'patrol':
      self.rect.x += self.patrol_speed * self.direction
      if self.rect.right > 700:
        self.direction = -1 
      elif self.rect.left < 100:
        self.direction = 1 
    
    elif self.state == 'chase':
      if player.rect.centerx > self.rect.centerx:
        self.direction = 1
        self.rect.x += self.chase_speed 
      else:
        self.direction = -1
        self.rect.x -= self.chase_speed 
    
    elif self.state == 'attack':
      pass  
  
  def update(self, grid_data, player): 
    self.x_vel = self.speed * self.direction if self.can_act() else 0 
    self.check_collision(grid_data) 
    if self.hit_wall: 
      self.direction *= -1 
    self.set_state(self.pick_state()) 
    self.animate() 
    self.ai_move(player)
    
  

player = Player(50, 50)
enemy = Skeleton(100, 50) 
map_data = load_map()
tile_images = load_tile_images() 
camera_x = 0

while True:
  clock.tick(FPS) 
  screen.fill('black')
  screen.blit(background, (0,0))
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit() 
      sys.exit() 
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit()
      
      if event.key == pygame.K_r:
        map_data = load_map() 
      if event.key == pygame.K_h: 
        player.take_hit()
      if event.key == pygame.K_k:
        enemy.take_hit()
    
  player.update(map_data)  
  enemy.update(map_data, player) 
  
  draw_map(screen, map_data, tile_images, camera_x) 

  enemy.draw(camera_x)
  player.draw(camera_x) 
  pygame.display.update()
