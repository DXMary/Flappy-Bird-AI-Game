import pygame, sys
import neat
import time
import os
import random
import pickle
from buttons import Button


# WIN SETUP

WIN_WIDTH = 480
WIN_HEIGHT = 730
FLOOR = 640

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("AI MODE")

# FONT SETUP

pygame.font.init() 

MAIN_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird AI Game/Assets/AquireBold-8Ma60.otf", 25)
SEC_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird AI Game/Assets/AquireBold-8Ma60.otf", 40)
DES_FONT = pygame.font.Font("/Users/user/Desktop/Flappy Bird AI Game/Assets/Aquire-BW0ox.otf", 20)

DRAW_LINES = False

# INITIATE CONSTANTS, IMAGES AND MUSIC

base_img = pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Base.png"))
bird_imgs = [pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Bluebird-upflap.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Bluebird-midflap.png"))), 
            pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Bluebird-downflap.png")))]
pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Pipe.png")))
bg_img = pygame.image.load(os.path.join("Img", "/Users/user/Desktop/Flappy Bird AI Game/Assets/Background.jpeg"))
bg_music = [pygame.mixer.init(),pygame.mixer.music.load("/Users/user/Desktop/Flappy Bird AI Game/Assets/Background-music.mp3"),
        pygame.mixer.music.set_volume(0.1),
        pygame.mixer.music.play(-1)]
white = (255, 255, 255)
black = (0, 0, 0)
red =  (255, 0, 0)

# GENERATIONS STARTING NUMBER 

gen = 1

# BIRD SETUP

class Bird:

    MAX_ROTATION = 25
    IMGS = bird_imgs
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y): 

        self.x = x
        self.y = y
        self.tilt = 0 
        self.tick_count = 0 
        self.vel = 0 
        self.height = self.y 
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):

        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):

        self.tick_count += 1

        displacement = self.vel*self.tick_count + 0.5*(3)*self.tick_count**2

        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16
        
        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    def draw(self, win):
        
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]  
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]  
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]  
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]  
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

# PIPE SETUP

class Pipe:

    GAP = 180
    VEL= 6
    win = WIN

    def __init__(self, x):

        self.x = x
        self.heigh = 0

        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):

        self.height = random.randrange(50,350)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):

        self.x -= self.VEL

    def draw(self, win):

        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):

        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True

        return False

# BASE SETUP

class Base:

    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img
    win = WIN

    def __init__(self, y):

        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):

        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):

        win.blit(self.IMG,(self.x1, self.y))
        win.blit(self.IMG,(self.x2, self.y))

def blitRotateCenter(surf, image, topleft, angle):

    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):

    if gen == 0:
        gen = 1
    win.blit(bg_img, (0, 0))
    
    for pipe in pipes:
        pipe.draw(win)
    
    base.draw(win)
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, red, (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, red, (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        bird.draw(win)

    score_label = MAIN_FONT.render("SCORE " + str(score),1, white)
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 20))
    score_label = MAIN_FONT.render("GENS " + str(gen-1),1, white)
    win.blit(score_label, (15, 20))
    score_label = MAIN_FONT.render("ALIVE " + str(len(birds)),1, white)
    win.blit(score_label, (15, 50))

    pygame.display.update()


def eval_genomes (genomes, config):

    global WIN, gen
    gen += 1
    
    nets = []
    birds = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(600)]
    score = 0

    clock = pygame.time.Clock()

    # MAIN GAME LOOP

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  
                pipe_ind = 1                                       

        for x, bird in enumerate(birds):  
            ge[x].fitness += 0.1
            bird.move()

            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  
                bird.jump()

        base.move()
        
        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            for bird in birds:
                if pipe.collide(bird):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
    
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        if score == 100:
            break                

# NEAT SETUP

def run(config_file):
    
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(eval_genomes, 50) 
    print('\nBest genome:\n{!s}'.format(winner))

# PATH TO CONFIG FILE

if __name__ == '__main__':

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)


