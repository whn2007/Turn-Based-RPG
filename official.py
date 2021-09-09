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
selected = None
turn_increased = False

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Crazy Cowboys')

#load font
game_font = pygame.font.Font("images/ui/PixeloidSans.ttf", 30)

#health bar colors
hp_bar_color = (191, 255, 64)
#back hp bar
hp_back = pygame.image.load("images/hp_bar/hp_back.png").convert_alpha()
hp_back_big = pygame.image.load("images/hp_bar/hp_back_big.png").convert_alpha()
hp_bar_height = 10
hp_bar_width = 80

#load images
#background image
image = pygame.image.load('images/backgrounds/forest.png').convert_alpha()
background_image = pygame.transform.scale(image,(image.get_width() * 2, image.get_height() * 2))

#skill button positions:
button_one_pos = (600,533)
button_two_pos = (710,533)
button_three_pos = (820,533)

#function for drawing background
def draw_background():
    screen.blit(background_image, (0, -1050))

#skill button clas
class Button():
    def __init__(self,name, pos):
        self.skill_buttons_list = [] #0: normal button, 1: pressed, 2: selected
            #load in skill buttons
        buttons = ("skills", "clicked", "selected")
        self.name = name
        self.pos = pos
        for button in buttons:
            temp_list = []
            for i in range(len(os.listdir(f"images/characters/{self.name}/buttons/{button}"))):
                image = pygame.image.load(f"images/characters/{self.name}/buttons/{button}/{i}.png").convert_alpha()
                temp_list.append(image)
            self.skill_buttons_list.append(temp_list)
        self.image = self.skill_buttons_list[0][0]
        self.initial_rect = self.image.get_rect(midbottom = self.pos)
        self.rect = self.initial_rect
        
    def draw(self):
        screen.blit(self.image, self.rect)

#unit class
class Character():
    def __init__(self, position, name, scale_x, scale_y, flip_image, enemy, max_hp, attk, speed, skill_one_hit, skill_two_hit):
        self.state = 0 #0: idle, 1: skill one, 2: skill two, 3: hurt, 4: death, 5: walk
        self.update_time = pygame.time.get_ticks()
        self.animation_list = []
        self.frame_index = 0
        self.name = name
        self.enemy = enemy
        self.max_hp = max_hp
        self.hp = max_hp
        self.attk = attk
        self.speed = speed
        #lets next character in turn know that they can play their turn
        self.animation_finished = True
        #frame where animations of skill one and skill two reach peak
        self.skill_one_hit = skill_one_hit
        self.skill_two_hit = skill_two_hit
        #check if skill was casted already
        self.skill_activated = False
        self.skill_one_button = Button(self.name, button_one_pos)
        self.skill_two_button = Button(self.name, button_two_pos)
        self.skill_three_button = Button(self.name, button_three_pos)
        self.skill_buttons = [self.skill_one_button,self.skill_two_button,self.skill_three_button]


        #load all animations
        animations = ("idle", "skill_one", "skill_two", "hurt", "death", "walk")
        for animation in animations:
            temp_list = []
            for i in range(len(os.listdir(f"images/characters/{self.name}/{animation}"))):
                image = pygame.image.load(f"images/characters/{self.name}/{animation}/{i}.png").convert_alpha()
                if flip_image:
                    image = pygame.transform.flip(image, True, False)
                image = pygame.transform.scale(image,(image.get_width() * scale_x, image.get_height() * scale_y))
                temp_list.append(image)
            self.animation_list.append(temp_list)
            
        self.image = self.animation_list[self.state][self.frame_index]
        #Collision box for sprites
        self.rect = self.image.get_rect(center = position)


    def draw(self):
        screen.blit(self.image, self.rect)

    #update sprite
    def update(self):
        global target
        global turn_increased
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
            global selected
            #prevents turn from increasing more than once per turn
            if self.state == 1 or self.state == 2:
                turn_increased = False
            # if character is dead, leave death animation on last frame
            if self.state == 4:
                self.frame_index = len(self.animation_list[self.state]) - 1
            else: self.idle()
            self.animation_finished = True
            selected = None

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
    
    #load in portrait
    def draw_portrait(self):
        image = pygame.image.load(f"images/characters/{self.name}/icons/portrait.png")
        portrait = pygame.transform.scale(image,(image.get_width() * 8, image.get_height() * 8))
        screen.blit(portrait, (0,360))

    def portrait_hp_bar(self):
        #draw hp bar next to portrait
        ratio = self.hp / self.max_hp
        screen.blit(hp_back_big, (210,505))
        pygame.draw.rect(screen, hp_bar_color, (210, 505, (hp_bar_width * 2) * ratio, (hp_bar_height * 2)))
        #converts name and draws it above portrait hp bar
        temp_lst = self.name.split("_")
        temp_lst = [each_string.capitalize() for each_string in temp_lst]
        new_name = " ".join(temp_lst)
        portrait_name = game_font.render(f"{new_name}", False, (255,255,255))
        screen.blit(portrait_name, (210,460))
    
    def draw_buttons(self):
        for button in self.skill_buttons:
            button.draw()

    def draw_character_ui(self):
        self.portrait_hp_bar()
        self.draw_portrait()
        self.draw_buttons()

#sort character list by speed and adds some RNG
def speed_sort(char_list):
    char_list.sort(reverse=True, key=lambda s: s.speed + random.randrange(-10,11))

#initiate characters
char1 = Character((400,320), "shock_sweeper", 6, 6, False, False, 50, 15, 15, 3, 0)
char2 = Character((600,315), "skeleton", 5, 5, True, True, 30, 10, 5, 8, 0)
char3 = Character((750,315), "skeleton", 5, 5, True, True, 30, 10, 5, 8, 0)

#intializes characters and sorts first turn by speed
char_list = [char1,char2, char3]
speed_sort(char_list)
ally_list = [char1]
enemy_list = [char2,char3]

#variables
turn = 0
clicked = False
char_turn = char_list[turn]
char_turn_prev = char_turn
turn_increased = False

#wait time for enemy action
wait_count = 0
wait_time = 60


run = True
while run:
    clock.tick(fps)

    #draw background
    draw_background()

    #draw character health bars
    char1.draw_hp_bar(325, 40)
    char2.draw_hp_bar(115, 35)
    char3.draw_hp_bar(115, 35)
    #draw hitbox for characters, debug
    # for char in char_list:
    #     charRect = [(char.rect.centerx-50), (char.rect.centery-25), 100, 125]
    #     pygame.draw.rect(screen, hp_bar_color, pygame.Rect(charRect))

    #variables
    mouse_pos = pygame.mouse.get_pos()
    pygame.mouse.set_visible(True)
    char_turn = char_list[turn]

    #draw fighters
    for char in char_list:
        char.update()
        char.draw()
    
    #skips dead character turns
    if char_turn.hp <= 0:
        if turn == len(char_list) - 1:
            speed_sort(char_list)
            turn = 0                       
        else: turn += 1

    #draw portrait and corresponding hp_bar
    if char_turn_prev.animation_finished:
        char_turn.draw_character_ui()
    else:
        char_turn_prev.draw_character_ui()


    #player action
    if clicked and char_turn_prev.animation_finished and not char_turn.enemy:
        #select skill and animate it

        for count, button in enumerate(char_turn.skill_buttons):
            if clicked == True and button.rect.collidepoint(mouse_pos) and not char_turn.enemy:
                selected = char_turn.skill_buttons[count]
                selected.image = button.skill_buttons_list[1][0]
                #moves button down a bit to show that it was pressed
                selected.rect = button.image.get_rect(midbottom = (button.pos[0],button.pos[1]))
        
        
        for count, enemy in enumerate(enemy_list):
            #fix collision box
            enemy_rect = [(enemy.rect.centerx-50), (enemy.rect.centery-25), 100, 125]
            if pygame.Rect(enemy_rect).collidepoint(mouse_pos) and enemy.hp > 0:
                char_turn.animation_finished = False
                target = enemy_list[count]
                char_turn.skill_one()
                char_turn_prev = char_turn
                #update turn and makes sure it only runs once
                if turn_increased == False:
                    if turn == len(char_list) - 1:
                        speed_sort(char_list)
                        turn = 0                       
                    else: turn += 1
                    turn_increased = True

    #enemy action
    if char_turn.enemy and char_turn_prev.animation_finished:
        #ensures the next character cannot act before animiation is done
        wait_count += 1
        if wait_count >= wait_time:
            for char in ally_list:
                if char.hp > 0:
                    target = char
                break
            #prevents enemy from playing animation when player is dead
            if not target.enemy and target.hp > 0:
                char_turn.skill_one()
                char_turn.animation_finished = False
                wait_count = 0
                char_turn_prev = char_turn
                #update turn and makes sure it only runs once
                if turn_increased == False:
                    if turn == len(char_list) - 1:
                        speed_sort(char_list)
                        turn = 0                       
                    else: turn += 1
                    turn_increased = True

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