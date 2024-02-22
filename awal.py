import sys
import random
import pygame
from pygame.locals import *

pygame.init()

player_ship = 'plyship.png'
enemy_ship = 'enemyship.png'
ufo_ship = 'ufo.png'
player_bullet = 'pbullet.png'
enemy_bullet = 'enemybullet.png'

screen = pygame.display.set_mode((0, 0), FULLSCREEN)
s_width, s_height = screen.get_size()

clock = pygame.time.Clock()
FPS = 60

background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()

sprite_group = pygame.sprite.Group()

class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([x, y])
        self.image.fill('white')
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        self.rect.x += 1
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

class Player(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.health = 10

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.rect.x = mouse[0]
        self.rect.y = mouse[1]
    
    def shoot(self):
        bullet = PlayerBullet(player_bullet)
        mouse = pygame.mouse.get_pos()
        bullet.rect.x = mouse[0]
        bullet.rect.y = mouse[1]
        playerbullet_group.add(bullet)
        sprite_group.add(bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, s_width)
        self.rect.y = random.randrange(-500, 0)
        self.image.set_colorkey('black')
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = 3000
        self.target = None
        self.health = 5

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width)
            self.rect.y = random.randrange(-2000, 0)
        
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            if self.target:
                self.shoot(self.target)
            self.last_shot = now

    def shoot(self, target):
        enemybullet = EnemyBullet(enemy_bullet)
        enemybullet.rect.x = self.rect.x
        enemybullet.rect.y = self.rect.y
        dir_vector = pygame.math.Vector2(target.rect.centerx - self.rect.centerx, target.rect.centery - self.rect.centery).normalize()
        dir_vector *= 5
        enemybullet.velocity = dir_vector * 5
        enemybullet_group.add(enemybullet)
        sprite_group.add(enemybullet)

    def receive_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()

class Ufo(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200
        self.rect.y = 200
        self.move = 1
    
    def update(self):
        self.rect.x += self.move
        if self.rect.x > s_width:
            self.rect.x = -200
        elif self.rect.x < -200:
            self.rect.x = s_width

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        self.image = pygame.image.load(img)
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')

    def update(self):
        self.rect.y -= 5
        hits = pygame.sprite.spritecollide(self, enemy_group, True)
        for hit in hits:
            hit.receive_damage(1)
        if self.rect.y < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)

class Game:
    def __init__(self):
        self.run_game()

    def create_background(self):
        for i in range(20):
            x = random.randint(1, 8)
            background_image = Background(x, x)
            background_image.rect.x = random.randrange(0, s_width)
            background_image.rect.y = random.randrange(0, s_height)
            background_group.add(background_image)
            sprite_group.add(background_image)

    def create_player(self):
        self.player = Player(player_ship)
        player_group.add(self.player)
        sprite_group.add(self.player)

    def create_enemy(self):
        for i in range(10):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)
    
    def create_ufo(self):
        for i in range(1):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)
    
    def run_update(self):
        sprite_group.draw(screen)
        sprite_group.update()

    def run_game(self):
        self.create_background()
        self.create_player()
        self.create_enemy()
        self.create_ufo()
        while True:
            screen.fill('black')
            self.run_update()
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    self.player.shoot()
                    if event.key == K_ESCAPE:  
                        pygame.quit()
                        sys.exit()

            hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, True, True)
            for hit in hits:
                self.player.health -= 1
                if self.player.health <= 0:
                    print("Game Over")

            hits = pygame.sprite.spritecollide(self.player, enemy_group, True)
            for hit in hits:
                self.player.health -= 3
                if self.player.health <= 0:
                    print("Game Over")

            for enemy in enemy_group:
                if enemy.rect.y > s_height:
                    enemy.kill()
                    self.player.health -= 3
                    if self.player.health <= 0:
                        print("Game Over")
                elif pygame.sprite.collide_rect(enemy, self.player):
                    self.player.health -= 3
                    enemy.kill()
                    if self.player.health <= 0:
                        print("Game Over")

            pygame.display.update()
            clock.tick(FPS)

def main():
    game = Game()

if __name__ == '__main__':
    main()
 