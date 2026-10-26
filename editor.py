import pygame
import sys
from PIL import Image
import os 

pygame.init()

WIDTH = 800
HEIGHT = 600
side_margin = 300 

screen = pygame.display.set_mode((WIDTH+side_margin, HEIGHT)) 
pygame.display.set_caption('Tile Editor') 

background = pygame.image.load('assets/background_night .png')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
# hero = {
#   'idle' : 'assets/hero/frame_0.png',
#   'run' : [f'assets/hero/frame_{frame}.png' for frame in range(1,4)],  I am an idiot I do not need those now, I need those in the main file of the game.
# }

def sort_tiles(name):
  tiles_folder = f'assets/{name}'
  tiles = {} 
  
  for filename in os.listdir(tiles_folder):
    if filename.endswith('.png'):
      tile_name = os.path.splitext(filename)[0]
      
      file_path = os.path.join(tiles_folder, filename) 
      tiles[tile_name] = pygame.image.load(file_path).convert_alpha()
  return tiles 

def paint_tiles():
  hero = sort_tiles('hero')
  enemy = sort_tiles('enemy')
  
  screen.blit(background, (0,0)) 

def main():
  
  
  
    
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
        break 
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          sys.exit()
          break
    
    paint_tiles()
    pygame.display.update()
  pygame.quit()
  

if __name__ == '__main__':
  main()
