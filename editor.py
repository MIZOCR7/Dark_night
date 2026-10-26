import pygame
import sys
from PIL import Image
import os 

[img.save(f"assets/tiles/tile_{r}_{c}.png") for r, c, img in [(r, c, Image.open("assets/Tile Dungeon .png").crop((c * 16, r * 16, (c + 1) * 16, (r + 1) * 16))) for r in range(16) for c in range(16)] if img.getbbox()]



def main():
  
  pygame.init()

  WIDTH = 800
  HEIGHT = 600
  lower_margin = 100
  side_margin = 300 
  
  screen = pygame.display.set_mode((WIDTH+side_margin, HEIGHT+lower_margin)) 
  pygame.display.set_caption('Tile Editor')
  
  
  background = pygame.image.load('assets/background_night .png').convert_alpha()
  
    
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
        break 
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          sys.exit()
          break
    
    pygame.display.update()
  pygame.quit()
  

if __name__ == '__main__':
  main()
