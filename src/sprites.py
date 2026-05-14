import pygame
from src import config


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