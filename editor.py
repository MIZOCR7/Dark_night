import pygame
import sys
import os
import json

pygame.init()

WIDTH = 1000
HEIGHT = 900 
TILE_SIZE = 100
side_margin = 300

GRID_COLS = WIDTH // TILE_SIZE
GRID_ROWS = HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH+side_margin, HEIGHT))
pygame.display.set_caption('Tile Editor')
FPS = 60
timer = pygame.time.Clock()

background = pygame.image.load('assets/background_night .png')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
# hero = {
#   'idle' : 'assets/hero/frame_0.png',
#   'run' : [f'assets/hero/frame_{frame}.png' for frame in range(1,4)],  I am an idiot I do not need those now, I need those in the main file of the game.
# }


def draw_grid(camera_x):
  for c in range(GRID_COLS + 1):
    x = c * TILE_SIZE - camera_x % TILE_SIZE
    pygame.draw.line(screen, (80, 80, 80), (x, 0), (x, HEIGHT))
  for r in range(GRID_ROWS + 1):
    y = r * TILE_SIZE
    pygame.draw.line(screen, (80, 80, 80), (0, y), (WIDTH, y))

def save_map(grid_data, filename='map_data.json'):
  with open(filename, 'w') as f:
    json.dump(grid_data, f, indent=4)

def load_map(filename='map_data.json'):
  if os.path.exists(filename):
    with open(filename, 'r') as f:
      return json.load(f)
  return [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]


def sort_tiles(name):
  tiles_folder = f'assets/{name}'
  tiles = {}

  for filename in os.listdir(tiles_folder):
    if filename.endswith('.png'):
      tile_name = os.path.splitext(filename)[0]

      file_path = os.path.join(tiles_folder, filename)
      tiles[tile_name] = pygame.image.load(file_path).convert_alpha()
  return tiles

def paint_tiles(tile_images, tile_previews, grid_data, sidebar_buttons, selected_tile, font, camera_x):
  screen.blit(background, (0,0))
  first_col = camera_x // TILE_SIZE
  for row, cells in enumerate(grid_data):
    for col in range(first_col, min(first_col + GRID_COLS + 1, len(cells))):
      tile_name = cells[col]
      if tile_name in tile_images:
        screen.blit(tile_images[tile_name], (col * TILE_SIZE - camera_x, row * TILE_SIZE))

  draw_grid(camera_x)
  pygame.draw.rect(screen, (35, 35, 35), (WIDTH, 0, side_margin, HEIGHT))
  for rect, tile_name, _ in sidebar_buttons:
    screen.blit(tile_previews[tile_name], rect)
    if tile_name == selected_tile:
      pygame.draw.rect(screen, (255, 220, 80), rect, 3)
  for idx, text in enumerate(('LMB: paint  RMB: erase', 'Ctrl+S: save  Ctrl+O: load', 'Left/Right: move')):
    screen.blit(font.render(text, True, (230, 230, 230)), (WIDTH + 14, HEIGHT - 55 + idx * 24))


def main():
  tile_dict = sort_tiles('tiles')
  tile_names = sorted(tile_dict.keys())
  tile_images = {
    name: pygame.transform.scale(tile_dict[name], (TILE_SIZE, TILE_SIZE))
    for name in tile_names
  }
  button_size = 48
  font = pygame.font.Font(None, 22)
  tile_previews = {
    name: pygame.transform.scale(tile_dict[name], (button_size, button_size))
    for name in tile_names
  }
  
  selected_tile = tile_names[0] if tile_names else None
  grid_data = load_map()
  camera_x = 0

  def extend_map():
    required_cols = camera_x // TILE_SIZE + GRID_COLS
    for row in grid_data:
      row.extend([None] * max(0, required_cols - len(row)))

  extend_map()

  button_margin = 8
  buttons_per_row = 5

  sidebar_buttons = []
  for idx, t_name in enumerate(tile_names):
    col = idx % buttons_per_row
    row = idx // buttons_per_row
    x = WIDTH + 14 + col * (button_size + button_margin)
    y = 50 + row * (button_size + button_margin)
    rect = pygame.Rect(x, y, button_size, button_size)
    sidebar_buttons.append((rect, t_name, idx))

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pygame.quit()
          sys.exit()
        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
          save_map(grid_data)
        if event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
          grid_data = load_map()
          extend_map()
        if event.key == pygame.K_RIGHT:
          camera_x += TILE_SIZE
          extend_map()
        if event.key == pygame.K_LEFT:
          camera_x = max(0, camera_x - TILE_SIZE)
      if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
          for rect, tile_name, _ in sidebar_buttons:
            if rect.collidepoint(event.pos):
              selected_tile = tile_name
              break
          else:
            x, y = event.pos
            col, row = (x + camera_x) // TILE_SIZE, y // TILE_SIZE
            if 0 <= x < WIDTH and 0 <= col < len(grid_data[0]) and 0 <= row < GRID_ROWS and selected_tile:
              grid_data[row][col] = selected_tile
        elif event.button == 3:
          x, y = event.pos
          col, row = (x + camera_x) // TILE_SIZE, y // TILE_SIZE
          if 0 <= x < WIDTH and 0 <= col < len(grid_data[0]) and 0 <= row < GRID_ROWS:
            grid_data[row][col] = None

    paint_tiles(tile_images, tile_previews, grid_data, sidebar_buttons, selected_tile, font, camera_x)
    pygame.display.update()
    timer.tick(FPS)
  pygame.quit()


if __name__ == '__main__':
  main()
