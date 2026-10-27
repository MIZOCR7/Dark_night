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
    self.rect = (self.x, self.y, 50, 50)
    
    
  def draw(self):
    pygame.draw.rect(screen, 'red', self.rect)
  
  def update(self):
    self.draw() 


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
      
