import pygame


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet_path, frame_width=64, frame_height=64, frame_count=32, animation_speed=100):
        super().__init__()
        
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.frames = []
        self.load_frames(frame_count)
        
        self.current_frame = 0
        self.animation_time = 0
        self.animation_speed = animation_speed  # milliseconds per frame
        
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
    
    def load_frames(self, frame_count):
        for i in range(frame_count):
            frame_rect = pygame.Rect(i * self.frame_width, 0, self.frame_width, self.frame_height)
            frame_image = self.sprite_sheet.subsurface(frame_rect)
            self.frames.append(frame_image)
    
    def update(self, dt):
        self.animation_time += dt
        
        if self.animation_time >= self.animation_speed:
            self.animation_time = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
