import pygame
from src import config

def extractSprite(sheet_path, grid_x, grid_y, cell_w, cell_h):
    """
    Cuts a building out of your specified local directory images.
    """
    try:
        # 1. Load the specific image sheet
        full_sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"CRITICAL: Could not load building image at {sheet_path}. Check path!")
        # Fallback: Create a colored square so the game doesn't crash if path is wrong
        fallback = pygame.Surface((cell_w * config.GRID_CELL_SIZE, cell_h * config.GRID_CELL_SIZE))
        fallback.fill((255, 0, 0))
        return fallback

    # 2. Calculate pixel coordinates inside the image sheet
    # Adjust 'SPRITE_SIZE_ON_SHEET' if the spaces on your JPEG are larger/smaller than 32px
    SPRITE_SIZE_ON_SHEET = 64  # Assumes each grid row/col on your JPG is roughly 64px wide

    pixel_x = grid_x * SPRITE_SIZE_ON_SHEET
    pixel_y = grid_y * SPRITE_SIZE_ON_SHEET
    pixel_w = cell_w * SPRITE_SIZE_ON_SHEET
    pixel_h = cell_h * SPRITE_SIZE_ON_SHEET

    # 3. Slice the rectangle out of the sheet
    building_surf = pygame.Surface((pixel_w, pixel_h), pygame.SRCALPHA)
    building_surf.blit(full_sheet, (0, 0), (pixel_x, pixel_y, pixel_w, pixel_h))

    # 4. Scale it to match your game world's target cell size (32px)
    target_w = cell_w * config.GRID_CELL_SIZE
    target_h = cell_h * config.GRID_CELL_SIZE
    building_surf = pygame.transform.scale(building_surf, (target_w, target_h))

    return building_surf

# Sprite = pygame.image.load(r"D:\Year 2.2\ISE\1891569.jpg")
# Foundation= extractSprite(Sprite,0,0,1,1)
# Wall= extractSprite(Sprite,1,0,2,1)
# Tower= extractSprite(Sprite,2,0,1,2)
# House= extractSprite(Sprite,3,0,2,2)
# Workshop= extractSprite(Sprite,4,0,3,2)
# Mansion= extractSprite(Sprite,5,0,3,3)
# Palace= extractSprite(Sprite,6,0,4,4)o
# Observatory= extractSprite(Sprite,7,0,2,4)

class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x=None, y=None, sprite_sheet_path=None, frame_width=None, frame_height=None, frame_count=None, animation_speed=None, scale=None):
        super().__init__()
        
        if x is None or y is None:
            x, y = config.get_moon_position()
        sprite_sheet_path = sprite_sheet_path or config.MOON_SPRITESHEET
        frame_width = frame_width or config.FRAME_WIDTH
        frame_height = frame_height or config.FRAME_HEIGHT
        frame_count = frame_count or config.FRAME_COUNT
        animation_speed = animation_speed or config.ANIMATION_SPEED_MS
        scale = scale or config.MOON_SCALE
        
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = []
        self.load_frames(frame_count, scale)
        
        self.current_frame = 0
        self.animation_time = 0
        self.animation_speed = animation_speed
        
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
    
    def load_frames(self, frame_count, scale):
        for i in range(frame_count):
            frame_rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame_image = self.sprite_sheet.subsurface(frame_rect)
            if scale != 1.0:
                new_size = (int(self.frame_width * scale), int(self.frame_height * scale))
                frame_image = pygame.transform.scale(frame_image, new_size)
            self.frames.append(frame_image)
    
    def set_position(self, position):
        x, y = position
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self, dt):
        self.animation_time += dt
        
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

