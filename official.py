import pygame
#os used to access files
import os
#random used for some RNG
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

#game window
screen_width = 960
screen_height = 540

#global variables
target = None

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Crazy Cowboys')


#health bar colors
hp_bar_color = (191, 255, 64)
#back hp bar
hp_back = pygame.image.load("images/hp_bar/hp_back.png").convert_alpha()
hp_bar_height = 10
hp_bar_width = 80

#load images
#background image
image = pygame.image.load('images/backgrounds/forest.png').convert_alpha()
background_image = pygame.transform.scale(image,(image.get_width() * 2, image.get_height() * 2))

#function for drawing background
def draw_background():
    screen.blit(background_image, (0, -1050))

#fighter class
class Character():
    def __init__(self, position, name, scale_x, scale_y, flip_image, enemy, max_hp, attk, skill_one_hit, skill_two_hit):
        self.state = 0 #0: idle, 1: skill one, 2: skill two, 3: hurt, 4: death, 5: walk
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        self.frame_index = 0
        self.enemy = enemy
        self.max_hp = max_hp
        self.hp = max_hp
        self.attk = attk
        #lets next character in turn know that they can play their turn
        self.animation_finished = True
        #frame where animations of skill one and skill two reach peak
        self.skill_one_hit = skill_one_hit
        self.skill_two_hit = skill_two_hit
        #check if skill was casted already
        self.skill_activated = False


    #load all animations
        animations = ("idle", "skill_one", "skill_two", "hurt", "death", "walk")
        for animation in animations:
            temp_list = []
            for i in range(len(os.listdir(f"images/characters/{name}/{animation}"))):
                image = pygame.image.load(f"images/characters/{name}/{animation}/{i}.png").convert_alpha()
                if flip_image:
                    image = pygame.transform.flip(image, True, False)
                image = pygame.transform.scale(image,(image.get_width() * scale_x, image.get_height() * scale_y))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        
        self.image = self.animation_list[self.state][self.frame_index]
        #Collision box for sprites
        self.rect = self.image.get_rect()
        self.rect.center = position

    def draw(self):
        screen.blit(self.image, self.rect)

    #update sprite
    def update(self):
        global target
        animation_cooldown = 100
        #handle animation
        #update image
        self.image = self.animation_list[self.state][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        #calculates damage animations at the frame when the attack hits
        if self.state == 1 and self.frame_index == self.skill_one_hit:
            #if the skill has not been yet casted:
            if not self.skill_activated:
                damage = self.attk
                target.hp -= damage
                if target.hp <= 0:
                    target.death()
                else:
                    target.hurt()
                self.skill_activated = True

        if self.frame_index >= len(self.animation_list[self.state]) - 1:
            # if character is dead, leave death animation on last frame
            if self.state == 4:
                self.frame_index = len(self.animation_list[self.state]) - 1
            else: self.idle()
            self.animation_finished = True

    def idle(self):
        #set variable to idle animation
        self.state = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
    
    def skill_one(self):
        #allows for skill to be casted in update function
        self.skill_activated = False
        self.state = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def skill_two(self):
        #allows for skill to be casted in update function
        self.skill_activated = False
        self.state = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        #set variables to hurt animation
        self.state = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        #set variables to death animation
        self.state = 4
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def draw_hp_bar(self, added_x, added_y):
        #update with new health
        #calculate health ratio
        ratio = self.hp / self.max_hp
        screen.blit(hp_back, (self.rect.x + added_x, self.rect.y + added_y))
        pygame.draw.rect(screen, hp_bar_color, (self.rect.x + added_x, self.rect.y + added_y, hp_bar_width * ratio, hp_bar_height))


#initiate characters
char1 = Character((400,320), "shock_sweeper", 6, 6, False, False, 50, 7, 3, 0)
char2 = Character((600,315), "skeleton", 5, 5, True, True, 30, 10, 7, 0)

char_list = [char1,char2]
ally_list = [char1]
enemy_list = [char2]

#variables
turn = 0
clicked = False
char_turn = char_list[turn]
char_turn_prev = char_turn
#hp bars
#wait time for enemy action
wait_count = 0
wait_time = 100


run = True
while run:

    clock.tick(fps)

    #draw background
    draw_background()

    #draw character health bars
    char1.draw_hp_bar(325, 55)
    char2.draw_hp_bar(115, 40)

    #variables
    mouse_pos = pygame.mouse.get_pos()
    pygame.mouse.set_visible(True)
    char_turn = char_list[turn]

    #draw fighters
    for char in char_list:
        char.update()
        char.draw()
    
    #player action
    if clicked and char_turn_prev.animation_finished and not char_turn.enemy and char_turn.hp > 0:
        for count, enemy in enumerate(enemy_list):
            if enemy.rect.collidepoint(mouse_pos) and enemy.hp > 0:
                target = enemy_list[count]
                char_turn.skill_one()
                char_turn_prev = char_turn
                #update turn
                if turn == len(char_list) - 1: turn = 0                       
                else: turn += 1

    
    #enemy action
    if char_turn.enemy and char_turn_prev.animation_finished and char_turn.hp > 0:
        #ensures the next character cannot act before animiation is done
        char_turn.animation_finished = False
        wait_count += 1
        if wait_count >= wait_time:
            for char in ally_list:
                if char.hp > 0:
                    target = char
                break
            char_turn.skill_one()
            wait_count = 0
            char_turn_prev = char_turn
            #update turn
            if turn == len(char_list) - 1: turn = 0                       
            else: turn += 1


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #get mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
        

    pygame.display.update()

pygame.quit()