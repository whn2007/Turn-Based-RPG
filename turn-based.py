import pygame
import sys
import os
import random

clock = pygame.time.Clock()
fps = 60

from pygame.constants import FULLSCREEN, KSCAN_RIGHT

pygame.init()   

#screen and ui variables
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width,screen_height))#,FULLSCREEN)
pygame.display.set_caption("Battle")

#define game variables:
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 10

#define fonts
font = pygame.font.SysFont('Times New Roman', 26)

#define colors
red = (255, 0, 0)
green = (0, 255, 0)

#load background
background_image = pygame.image.load("images/backgrounds/forest.png").convert_alpha()
#load bottom UI
panel_image = pygame.image.load("images/ui/panel.png").convert_alpha()


#create function for drawing text
def draw_text(text, font, text_col, x, y):
    image = font.render(text,True,text_col)
    screen.blit(image, (x, y))

#draw UI
def draw_background():
    screen.blit(background_image, (0,-370))

def draw_panel():
    #draw panel rectangle
    screen.blit(panel_image,(0,screen_height-bottom_panel))
    #show player stats
    draw_text(f"{shock_sweeper.name} HP: {shock_sweeper.hp}", font, red, 80, screen_height - bottom_panel + 30)
    for count, i in enumerate(enemy_list):
        #show name and health
        draw_text(f"{i.name} HP: {i.hp}", font, red, 510, (screen_height - bottom_panel + 20) + (count * 50))

#player inputs
def screen_input():
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()

#Fighter Class
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions, enemy, scale_x = None, scale_y = None):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        #setting frame 
        self.frame_index = 0
        self.action = 0 #0: idle, 1:attack, 2:hurt 3:death
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        
        #load idle images
        temp_list = []
        for i in range(len(os.listdir(f"images/characters/{self.name}/idle"))):
            image = pygame.image.load(f"images/characters/{self.name}/idle/{i}.png").convert_alpha()
            if enemy:
                image = pygame.transform.flip(image, True, False)
            image = pygame.transform.scale(image,(image.get_width() * scale_x, image.get_height() * scale_y))
            temp_list.append(image)
        self.animation_list.append(temp_list)

        #load attack images
        temp_list = []
        for i in range(len(os.listdir(f"images/characters/{self.name}/attack"))):
            image = pygame.image.load(f"images/characters/{self.name}/attack/{i}.png").convert_alpha()
            if enemy:
                image = pygame.transform.flip(image, True, False)
            image = pygame.transform.scale(image,(image.get_width() * scale_x, image.get_height() * scale_y))
            temp_list.append(image)
        self.animation_list.append(temp_list)


        self.image = self.animation_list[self.action][self.frame_index]
        #Collision box for sprites
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

    #update sprite
    def update(self):
        animation_cooldown = 100
        #handle animation
        #update image
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        if self.frame_index >= len(self.animation_list[self.action]):
            self.idle()

    def idle(self):
        #set variable to attack animation
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()


    def attack(self,target):
        #deal damage
        rand = random.randint(-5,5)
        damage = self.strength + rand
        target.hp -= damage
        #check if target has died
        
        #set variable to attack animation
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    #display on screen
    def draw(self): 
        screen.blit(self.image, self.rect)

class Health_Bar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp
    
    def draw(self, hp): 
        #update with new help
        self.hp = hp
        #calculate health ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x,self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x,self.y, 150 * ratio, 20))
        

#initializing player and enemies
shock_sweeper = Fighter(300,290,"shock_sweeper", 30, 10, 3, False, 5, 5)
skeleton1 = Fighter(550, 295, "skeleton", 20, 6, 1, True, 4, 4)
skeleton2 = Fighter(650, 295, "skeleton", 20, 6, 1, True, 4, 4)

enemy_list = [skeleton1,skeleton2]

#health bars
shock_sweeper_health_bar = Health_Bar(80, screen_height-bottom_panel + 60, shock_sweeper.hp, shock_sweeper.max_hp)
skeleton1_health_bar = Health_Bar(510, screen_height-bottom_panel + 50, skeleton1.hp, skeleton1.max_hp)
skeleton2_health_bar = Health_Bar(510, screen_height-bottom_panel + 100, skeleton2.hp, skeleton2.max_hp)

run = True
while run:
    
    #limit fps
    clock.tick(fps)
    
    #draw background
    draw_background()

    #draw panel ui
    draw_panel()
    shock_sweeper_health_bar.draw(shock_sweeper.hp)
    skeleton1_health_bar.draw(skeleton1.hp)
    skeleton2_health_bar.draw(skeleton2.hp)

    #draw characters
    shock_sweeper.update()
    shock_sweeper.draw()
    for enemy in enemy_list:
        enemy.update()
        enemy.draw()

    
    #player action
    if shock_sweeper.alive:
        if current_fighter == 1:
            action_cooldown += 1
            if action_cooldown >= action_wait_time:
                #look for player action
                #attack
                shock_sweeper.attack(skeleton1)
                current_fighter += 1
                action_cooldown = 0
    
    #enemy action
    for count, enemy in enumerate(enemy_list):
        if current_fighter == 2 + count:
            if enemy.alive == True:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    #attack
                    enemy.attack(shock_sweeper)
                    current_fighter += 1
                    action_cooldown = 0
            else:
                current_fighter += 1
    
    #if all fighters have had a turn, reset
    if current_fighter > total_fighters:
        current_fighter == 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        screen_input()


    pygame.display.update()