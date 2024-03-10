# Brick Breaker
# Luna Nguyen
# Block 4

import pygame, random, sys, math, time, os
from pygame.locals import *
from random import choice, randint
from os import walk

# setting up the window
pygame.init()
SCREENWIDTH, SCREENHEIGHT = 1200, 750
windowSurfaceOBj = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Brick Breaker')
BGImage = pygame.image.load("graphics/other/bg1.jpg")

#list of scores
scores = [0]

# List of upgrades
UPGRADES = ['speed', 'size', 'heart', 'laser']

#define game variables
game_over = False
level = 0
screen = 0
game_start = True
Clicked_Space = False

# map of blocks' positions with 3 levels
BLOCK_MAP =[[
			'                ',
			' 666666666666666',
			'                ',
			'555555555555555 ',
			'                ',
			' 444444444444444',
			'                ',
			'333333333333333 ',
			'                ',
			' 222222222222222',
			'                ',
			'111111111111111 ',
			'                ',
			'                ',
			'                ',
			'                ',
			'                ',
			'                '],
			[
			'                ',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4 3333 4 222',
			'555 4      4 222',
			'    44444444    ',
			'    44444444    ',
			'    44444444    ',
			'                ',
			'                ',
			'                ',
			'                ',
			'                ',
			'                '],
			[
			'                ',
			'7777777777777777',
			'6666666666666666',
			'5555555555555555',
			'4444444444444444',
			'3333333333333333',
			'2222222222222222',
			'2222222222222222',
			'1111111111111111',
			'1111111111111111',
			'1111111111111111',
			'1111111111111111',
			'                ',
			'                ',
			'                ',
			'                ',
			'                ',
			'                ']]
			
COLOR_LEGEND = {
			'1': 'blue',
			'2': 'green',
			'3': 'pink',
			'4': 'dark blue',
			'5': 'purple',
			'6': 'red',
			'7': 'yellow'
			}
			
GAP_SIZE = 2
BLOCK_HEIGHT = SCREENHEIGHT / len(BLOCK_MAP[0]) - GAP_SIZE
BLOCK_WIDTH = SCREENWIDTH / len(BLOCK_MAP[0][1]) - GAP_SIZE

#Create a class for drawing blocks and player graphics
class SurfaceMaker:
	# import all the graphics
	def __init__(self):
		for index, info in enumerate(walk('graphics/blocks')):
			if index == 0:
				self.assets = {}
				for color in info[2]:
					color_type = []
					color_type.append(color.split('.')[0])
					full_path = "graphics/blocks/" + color_type[0] + ".png"
					surf = pygame.image.load(full_path).convert_alpha()
					self.assets[color_type[0]] = surf			
	
	
	
	def get_surf(self, block_type, size):
		image = pygame.Surface(size)
		sides = self.assets[block_type]
		image.set_colorkey((0,0,0))
		
		# draw the blocks and player
		if block_type == 'player':
			scaled_image = pygame.transform.scale(sides, size)
			image.blit(scaled_image,(0,0))
		else:
			scaled_image = pygame.transform.scale(sides, (BLOCK_WIDTH,BLOCK_HEIGHT))
			image.blit(scaled_image,(0,0))
		
		# return that image to the blocks or the player
		return image

# Create a class for upgrades
class Upgrade(pygame.sprite.Sprite):
	def __init__(self,pos,upgrade_type,groups):
		super().__init__(groups)
		self.upgrade_type = upgrade_type
		self.image = pygame.image.load(f'graphics/upgrades/{upgrade_type}.png').convert_alpha()
		self.rect = self.image.get_rect(midtop = pos)
		
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 300
		
	def update(self,dt):
		self.pos.y += self.speed*dt
		self.rect.y = round(self.pos.y)
		
		if self.rect.top > SCREENHEIGHT + 100:
			self.kill()

# Create a class for the projectiles
class Projectile(pygame.sprite.Sprite):
	def __init__(self,pos,surface,groups):
		super().__init__(groups)
		self.image = surface
		self.rect = self.image.get_rect(midbottom = pos)
		
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 300
		
	def update(self,dt):
		self.pos.y -= self.speed * dt
		self.rect.y = round(self.pos.y)
		
		if self.rect.bottom <= -100:
			self.kill()

# Create a class for the paddle
class Player(pygame.sprite.Sprite):
	def __init__(self,groups,surfacemaker):
		super().__init__(groups)
		
		#setup
		self.display_surface = pygame.display.get_surface()
		self.surfacemaker = surfacemaker
		self.image = self.surfacemaker.get_surf('player', (SCREENWIDTH // 8, SCREENHEIGHT // 20))
		
		#position
		self.rect = self.image.get_rect(midbottom = (SCREENWIDTH // 2, SCREENHEIGHT - 20))
		self.old_rect = self.rect.copy()
		self.direction = pygame.math.Vector2()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		self.speed = 300
		
		self.hearts = 3
		
		# laser
		self.laser_amount = 0
		self.laser_surf = pygame.image.load('graphics/other/laser.png').convert_alpha()
		self.laser_rects = []
		
		# size upgrade variable. These variables help the upgrade to last for 2 seconds
		self.length_time = 0
		
	# function for moving left and right
	def input(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_RIGHT]:
			self.direction.x = 1
		elif keys[pygame.K_LEFT]:
			self.direction.x = -1
		else:
			self.direction.x = 0	
	
	# function for not letting the paddle moves off screen
	def screen_constraint(self):
		if self.rect.right > SCREENWIDTH:
			self.rect.right = SCREENWIDTH
			self.pos.x = self.rect.x
		if self.rect.left < 0:
			self.rect.left = 0
			self.pos.x = self.rect.x			
	
	def upgrade(self, upgrade_type):
		# increase the speed upgrade
		if upgrade_type == 'speed':
			self.speed += 50
		# add a heart upgrade
		if upgrade_type == 'heart':
			self.hearts += 1
		# increase the paddle's width for a certain time upgrade
		if upgrade_type == 'size':
			new_width = (SCREENWIDTH // 8) * 1.5
			self.image = self.surfacemaker.get_surf('player', (new_width, self.rect.height))
			self.rect = self.image.get_rect(center = self.rect.center)
			self.pos.x = self.rect.x
			self.length_time = pygame.time.get_ticks()
		# laser upgrade	
		if upgrade_type == 'laser':
			self.laser_amount = 2
			
	def display_lasers(self):
		self.laser_rects = []
		if self.laser_amount > 0:
			divider_length = self.rect.width / (self.laser_amount + 1)
			for i in range(self.laser_amount):
				x = self.rect.left + divider_length * (i + 1)
				laser_rect = self.laser_surf.get_rect(midbottom = (x,self.rect.top))
				self.laser_rects.append(laser_rect)
				
			for laser_rect in self.laser_rects:
				self.display_surface.blit(self.laser_surf, laser_rect)
	
	def update(self, dt):
		self.old_rect = self.rect.copy()
		self.input()
		self.pos.x += self.direction.x * self.speed * dt
		self.rect.x = round(self.pos.x)
		self.screen_constraint()
		self.display_lasers()
		
class Ball(pygame.sprite.Sprite):
	def __init__(self, groups, player, blocks):
		super().__init__(groups)
		
		# collision objects
		self.player = player
		self.blocks = blocks
		
		# graphics setup
		self.image = pygame.image.load("graphics/other/ball1.png").convert_alpha()
		
		# position setup
		self.rect = self.image.get_rect(midbottom = player.rect.midtop)
		self.old_rect = self.rect.copy()
		self.pos = pygame.math.Vector2(self.rect.topleft)
		# when launched, the ball always move up, but randomly move left or right
		self.direction = pygame.math.Vector2((choice((1,-1)),-1))
		self.speed = 400
		
		# active (moving ball)
		self.active = False
		
		# sounds
		self.impact_sound = pygame.mixer.Sound('sounds/impact.wav')
		self.impact_sound.set_volume(0.1)
		
		self.fail_sound = pygame.mixer.Sound('sounds/fail.wav')
		self.fail_sound.set_volume(0.1)
		
		# points
		self.points = 0
	
	# function for ball colliding with the window boundary
	# if the ball collides left, right or top boundary, it bounces back in the opposite direction.
	# if the ball goes out of boundary at the bottom and there's still heart, the ball returns to stay on top of the paddle.
	def window_collision(self,direction):
		if direction == 'horizontal':
			if self.rect.left < 0:
				self.rect.left = 0
				self.pos.x = self.rect.x
				self.direction.x *= -1
			
			if self.rect.right > SCREENWIDTH:
				self.rect.right = SCREENWIDTH
				self.pos.x = self.rect.x
				self.direction.x *= -1
				
		if direction == 'vertical':
			if self.rect.top < 0:
				self.rect.top = 0
				self.pos.y = self.rect.y
				self.direction.y *= -1
			
			if self.rect.bottom > SCREENHEIGHT:
				self.active = False
				self.direction.y = -1
				self.player.hearts -= 1
				self.fail_sound.play()
	
	def collision(self, direction):
		# find overlapping objects. The overlap_sprites includes all the items that the ball collides with.
		overlap_sprites = pygame.sprite.spritecollide(self,self.blocks,False)
		if self.rect.colliderect(self.player.rect):
			overlap_sprites.append(self.player)
		
		# if the ball collides with another sprite horizontally or vertically, it will identify which direction the ball comes from
		# then moves the opposite way.
		# only block sprite has 'health' attribute. So, if collides, block's health -1 and points +1
		if overlap_sprites:
			if direction == 'horizontal':
				for sprite in overlap_sprites:
					if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
						self.rect.right = sprite.rect.left - 1
						self.pos.x = self.rect.x
						self.direction.x *= -1
						self.impact_sound.play()
						
					if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
						self.rect.left = sprite.rect.right + 1
						self.pos.x = self.rect.x
						self.direction.x *= -1
						self.impact_sound.play()
				
					if getattr(sprite, 'health', None):
						sprite.get_damage(1)
						self.points += 1
				
			if direction == 'vertical':
				for sprite in overlap_sprites:
					if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
						self.rect.bottom = sprite.rect.top - 1
						self.pos.y = self.rect.y
						self.direction.y *= -1
						self.impact_sound.play()
						
					if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
						self.rect.top = sprite.rect.bottom + 1
						self.pos.y = self.rect.y
						self.direction.y *= -1
						self.impact_sound.play()
						
					if getattr(sprite, 'health', None):
						sprite.get_damage(1)
						self.points += 1
				
	def update(self,dt):
		# if the ball is moving
		if self.active:
			
			# normalize the vector direction to 1 so the ball's diagonal speed is same as the horizontal/vertical speed
			if self.direction.magnitude() != 0:
				self.direction = self.direction.normalize()
			
			# create old rect
			self.old_rect = self.rect.copy()
			
			# horizontal movement + collision
			self.pos.x += self.direction.x * self.speed * dt
			self.rect.x = round(self.pos.x)
			self.collision('horizontal')
			self.window_collision('horizontal')
			
			# vertical movement + collision
			self.pos.y += self.direction.y * self.speed * dt
			self.rect.y = round(self.pos.y)
			self.collision('vertical')
			self.window_collision('vertical')
			
		# if the ball is not moving, it stays on midtop of the paddle	
		else:
			self.rect.midbottom = self.player.rect.midtop
			self.pos = pygame.math.Vector2(self.rect.topleft)

class Block(pygame.sprite.Sprite):
	def __init__(self,block_type,pos,groups, surfacemaker, create_upgrade):
		super().__init__(groups)
		self.surfacemaker = surfacemaker
		self.image = self.surfacemaker.get_surf(COLOR_LEGEND[block_type], (BLOCK_WIDTH, BLOCK_HEIGHT))
		self.rect = self.image.get_rect(topleft = pos)
		self.old_rect = self.rect.copy()
		
		# damage information
		self.health = int(block_type)
		
		# upgrade
		self.create_upgrade = create_upgrade
		
	def get_damage(self, amount):
		self.health -= amount
			
		if self.health > 0:
			self.image = self.surfacemaker.get_surf(COLOR_LEGEND[str(self.health)], (BLOCK_WIDTH, BLOCK_HEIGHT))
		else:
			# 33.3% chances upgrade if appear if a block is destroyed
			if randint(0,10) < 3:
				self.create_upgrade(self.rect.center)
			self.kill()

class Label():	
	def __init__(self, x, y, size):
		self.font = pygame.font.Font(None, size)
		self.x, self.y = x, y

	def write (self, color, text):
		my_text = self.font.render(text, True, color)
		windowSurfaceOBj.blit(my_text, (self.x, self.y))
		
class Button():
	def __init__(self,x,y,image,image_pressed):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x,y)
		self.image_pressed = image_pressed
		self.rect_pressed = self.image_pressed.get_rect()
		self.rect_pressed.topleft = (x + 20 ,y + 20)
		
	def draw(self):
		
		action = False
		
		#get mouse position
		pos = pygame.mouse.get_pos()
		
		#draw button
		windowSurfaceOBj.blit(self.image, (self.rect.x, self.rect.y))
		
		#check mouseover and mouse click
		if self.rect.collidepoint(pos):
			windowSurfaceOBj.blit(self.image_pressed, (self.rect_pressed.x, self.rect_pressed.y))
			if pygame.mouse.get_pressed()[0] == 1:
				action = True		
		
		return action

#import bg sound
music = pygame.mixer.Sound('sounds/music2.wav')

# sprite group setup
all_sprites = pygame.sprite.Group()
block_sprites = pygame.sprite.Group()
upgrade_sprites = pygame.sprite.Group()
projectile_sprites = pygame.sprite.Group()

# set up
surfacemaker = SurfaceMaker()
player = Player(all_sprites, surfacemaker)
ball = Ball(all_sprites, player, block_sprites)
heart_surf = pygame.image.load('graphics/other/heart1.png').convert_alpha()
textbg = pygame.image.load('graphics/other/textbg.png').convert_alpha()
openingscreen = pygame.image.load('graphics/other/openingscreen.jpg').convert_alpha()
openingscreen_scaled = pygame.transform.scale(openingscreen, (SCREENWIDTH,SCREENHEIGHT))
textbg_scaled = pygame.transform.scale(textbg, (textbg.get_width() // 2, textbg.get_height()))
MyText = Label(SCREENWIDTH - textbg_scaled.get_width() + 5, 5, 40)

#load button images
button_img = pygame.image.load('graphics/other/button.png').convert_alpha()
button_pressed_img = pygame.image.load('graphics/other/button_pressed.png').convert_alpha()
#create restart button instance
button = Button(SCREENWIDTH // 2 - (button_img.get_width() // 2), SCREENHEIGHT * 2/3, button_img, button_pressed_img)

#projectile setup: import image and state variables so that projectiles fires at certain interval of time
projectile_surf = pygame.image.load('graphics/other/projectile.png').convert_alpha()
can_shoot = True
shoot_time = 0

#function for calculating highscores
def calc_highscores():
	scores.sort(reverse=True)
	high_scores = scores[0]
	return high_scores

#create upgrade
def create_upgrade(pos):
	upgrade_type = choice(UPGRADES)
	Upgrade(pos,upgrade_type,[all_sprites,upgrade_sprites])

#cycle through all rows and columns of BLOCK MAP
def stage_setup():
	for row_index, row in enumerate(BLOCK_MAP[level]):
		for col_index, col in enumerate(row):
			if col != ' ':
				# find the x and y position for each individual block
				y = row_index * (BLOCK_HEIGHT + GAP_SIZE) + GAP_SIZE // 2
				x = col_index * (BLOCK_WIDTH + GAP_SIZE) + GAP_SIZE // 2
				Block(col,(x,y),[all_sprites, block_sprites], surfacemaker, create_upgrade)
		
#display hearts
def display_hearts():
	for i in range(player.hearts):
		x = 2 + i * (heart_surf.get_width() + 2)
		windowSurfaceOBj.blit(heart_surf, (x,4))

#collision function for upgrades and player
def upgrade_collision():
	overlap_sprites = pygame.sprite.spritecollide(player, upgrade_sprites, True)
	for sprite in overlap_sprites:
		player.upgrade(sprite.upgrade_type)
		powerup_sound.play()

#create projectile for lasers.
count_shoot = 0
def create_projectile():
	laser_sound.play()
	global count_shoot
	for projectile in player.laser_rects:
		Projectile(projectile.midtop - pygame.math.Vector2(0,30),projectile_surf,[all_sprites, projectile_sprites])
		count_shoot += 1
		if count_shoot >= 6:
			player.laser_rects = []
			player.laser_amount = 0
			count_shoot = 0

# function for projectile to damage blocks
def projectile_block_collision():
	for projectile in projectile_sprites:
		overlap_sprites = pygame.sprite.spritecollide(projectile,block_sprites,False)
		if overlap_sprites:
			for sprite in overlap_sprites:
				sprite.get_damage(1)
			projectile.kill()
			laserhit_sound.play()

#Check space input for StartScreen
def StartScreen_input():	
	for event in pygame.event.get():
		if event.type == QUIT:
				RunGame = False
				pygame.quit()
				sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				Clicked_Space = True
				return Clicked_Space

# Screen for Starting the game
def StartScreen():
	global screen
	music.set_volume(0.06)
	music.play(loops = -1)
	windowSurfaceOBj.blit(openingscreen_scaled, (0, 0))
	SpaceText1 = Label(SCREENWIDTH - 350, SCREENHEIGHT - 100 , 40)
	SpaceText1.write((255,255,255), "Click SPACE to Continue >>")
	if StartScreen_input() == True:
		screen += 1
	
# Instructions Screen
def Tutorial1():
	global screen
	windowSurfaceOBj.blit(BGImage, (0, 0))
	Tutorial.write((255,255,255,), "TUTORIAL")
	Instruction.write((255,255,255), "Move the paddle with arrow keys and destroy the bricks.")
	Instruction1.write((255,255,255), "Brick of different colors have different health value.")
	Instruction2.write((255,255,255), "Each brick hit is worth 1 point.")
	SpaceText.write((255,255,255), "Click SPACE to Continue >>")
	if StartScreen_input() == True:
		screen += 1
	
def Tutorial2():
	global screen
	windowSurfaceOBj.blit(BGImage, (0, 0))
	Tutorial.write((255,255,255,), "TUTORIAL")
	Instruction.write((255,255,255), "Destroying bricks will occasionally produce power-ups.")
	Instruction1.write((255,255,255), "Catch them with your paddle!")
	Instruction2.write((255,255,255), "Press SPACE to fire the laser if you have laser power-up.")
	SpaceText.write((255,255,255), "Click SPACE to Continue >>")
	if StartScreen_input() == True:
		screen += 1

def Tutorial3():
	global screen
	windowSurfaceOBj.blit(BGImage, (0, 0))
	Tutorial.write((255,255,255,), "TUTORIAL")
	Instruction.write((255,255,255), "Are you ready?")
	Instruction1.write((255,255,255), "Let's break some bricks and complete 3 levels!")
	Instruction2.write((255,255,255), "Press SPACE to release the ball.")
	SpaceText.write((255,255,255), "Click SPACE to Continue >>")
	if StartScreen_input() == True:
		screen += 1
	

# reset game after game over
def reset_game():
	player.hearts = 3
	player.rect.x = SCREENWIDTH // 2 - (SCREENWIDTH // 16)
	player.rect.y = SCREENHEIGHT - 20 - (SCREENHEIGHT // 20)
	if level == 0:
		ball.points = 0
				
	stage_setup()

# Screen for Game Over
def EndScreen():
	music.set_volume(0.06)
	music.play(loops = -1)
	player.laser_amount = 0
	windowSurfaceOBj.blit(BGImage, (0, 0))
	GameOverText = Label(SCREENWIDTH // 3.1, SCREENHEIGHT // 11 , 120)
	GameOverText.write((255,255,255), "GAME OVER")
	Highscores = Label(SCREENWIDTH // 3.1, SCREENHEIGHT // 3 , 100)
	Highscores.write((255,255,255), "HIGH SCORE : " + str(calc_highscores()))
	Scores = Label(SCREENWIDTH // 3.1, SCREENHEIGHT // 2 , 100)
	Scores.write((255,255,255), "SCORE : " + str(ball.points))

# Screen for winning 3 levels
def WinnerScreen():
	music.set_volume(0.1)
	music.play(loops = -1)
	player.laser_amount = 0
	windowSurfaceOBj.blit(BGImage, (0, 0))
	GameOverText = Label(SCREENWIDTH // 3.1, SCREENHEIGHT // 11 , 120)
	GameOverText.write((255,255,255), "YOU WIN!!")
	Scores = Label(SCREENWIDTH // 3.1, SCREENHEIGHT // 3 , 100)
	Scores.write((255,255,255), "SCORE : " + str(ball.points))

# Draw blocks layout
stage_setup()

RunGame = True
last_time = time.time()
while RunGame == True:
	
	# delta time
	dt = time.time() - last_time
	last_time = time.time()
	
	# draw background, Sprites objects, hearts and textbg
	windowSurfaceOBj.blit(BGImage, (0, 0))
	all_sprites.draw(windowSurfaceOBj)
	display_hearts()
	windowSurfaceOBj.blit(textbg_scaled, (SCREENWIDTH - textbg_scaled.get_width() - 5,1))
	
	MyText.write((255,255,255), str(ball.points))
	
	#sounds setup
	laser_sound = pygame.mixer.Sound('sounds/laser.wav')
	laser_sound.set_volume(0.1)
	
	powerup_sound = pygame.mixer.Sound('sounds/powerup.wav')
	powerup_sound.set_volume(0.1)
	
	laserhit_sound = pygame.mixer.Sound('sounds/laser_hit.wav')
	laserhit_sound.set_volume(0.02)
	
	# size upgrade cancels after 5 seconds
	if pygame.time.get_ticks() - player.length_time >= 5000:
		player.image = player.surfacemaker.get_surf('player', (SCREENWIDTH // 8, SCREENHEIGHT // 20))
		player.rect = player.image.get_rect(center = player.rect.center)
		player.pos.x = player.rect.x
	
	#Tutorial and start game screen:
	if game_start == True:
		Tutorial = Label(SCREENWIDTH // 3, SCREENHEIGHT // 11 , 120)
		Instruction = Label(SCREENWIDTH // 5, SCREENHEIGHT // 3, 40)
		Instruction1 = Label(SCREENWIDTH // 5, SCREENHEIGHT // 2.4, 40)
		Instruction2 = Label(SCREENWIDTH // 5, SCREENHEIGHT // 2, 40)
		SpaceText = Label(SCREENWIDTH * 3/4, SCREENHEIGHT // 1.5 , 25)
		if screen == 0:
			StartScreen()
		if screen == 1:
			Tutorial1()
		if screen == 2:
			Tutorial2()
		if screen == 3:
			Tutorial3()
		if screen == 4:
			game_start = False
			music.stop()
		
	#check if game is over (no hearts left)
	if player.hearts <= 0:
		game_over = True
	
	#check for gameover and reset
	if game_over == True:
		scores.append(ball.points)
		EndScreen()
		for event in pygame.event.get():
			if event.type == QUIT:
				RunGame = False
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					ball.active = False
		if button.draw() == True:
			game_over = False
			reset_game()
			music.stop()	
					
	#check for winning, moving to the next level
	if not block_sprites:
		if level != 3:
			level +=1
			reset_game()
		if level == 3:
			WinnerScreen()
	
	# Event pump for the X exit button, space button
	for event in pygame.event.get():
		if event.type == QUIT:
			RunGame = False
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				ball.active = True
				# create projectile when SPACE is pressed
				create_projectile()		
				
	
	# Update the game
	all_sprites.update(dt)
	upgrade_collision()		
	projectile_block_collision()
	
	pygame.display.update()

