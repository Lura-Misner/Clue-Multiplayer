import pygame


class Picture(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, picture_path):
        super().__init__()
        self.path = picture_path
        self.image = pygame.image.load(picture_path)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y

    def get_rect(self):
        return self.rect

    def get_path(self):
        return self.path

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def change_path(self, new_path):
        self.path = new_path
        self.image = pygame.image.load(self.path)