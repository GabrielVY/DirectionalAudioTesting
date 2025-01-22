import pygame
import math

TWO_PI = math.pi*2

pygame.init()

WIDTH, HEIGHT = 800, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))


# Load sound
sound1 = pygame.mixer.Sound("song.mp3")
soft_piano = pygame.mixer.Sound("softpiano.wav")

# Player variables
player_x = 400
player_y = 400
player_angle = math.radians(180)

MAX_CHANNELS = pygame.mixer.get_num_channels()

#Enum
ENVIRONMENT_CHANNEL = 0
PLAYER_CHANNEL = 1
INTERACTION_CHANNEL = 2
GENERAL_CHANNEL = [3, 4, 5, 6, 7]

# Priority system
# If all channels for a particular priority are being used then the most recent sound being played
# Replaces the oldest sound being played in the channel
# Some channels are reserved only for certain priorities, but if they are not being used and some sounds of other priorities want to be played
# They will, until some sound with a better priority occurs

channels = [pygame.mixer.Channel(x) for x in range(MAX_CHANNELS)]
free_channels = [c for c in channels] # Not being used at the moment

class Sound:

    channel_id = 0

    def __init__(self, pos, sound, base_volume=1, audible_range=200) -> None:
        self.pos = pos
        self.base_volume = base_volume
        self.audible_range = audible_range
        self.sound = sound
        self.channel = channels[Sound.channel_id]
        self.playing = True
        self.timestamp = 0 # Time into the sound
        Sound.channel_id += 1

    def play(self):
        self.channel.play(self.sound)

    def draw(self, surface):
        color = (0, 0, 200)

        if not self.playing:
            color = (200, 0, 0)

        # Draw sound source
        pygame.draw.circle(surface, color, self.pos, 8)
        pygame.draw.circle(surface, color, self.pos, self.audible_range, 1)

    def update(self, surface=None):
        self.timestamp += 1

        # Get sound source distance to the player
        x1, y1 = player_x, player_y
        x2, y2 = self.pos[0], self.pos[1]
        player_dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Check if player is in hearing range
        if player_dist > self.audible_range:
            # Stop playing channel
            if self.playing == True:
                #self.timestamp = pygame.mixer.music.get_pos() / 1000
                self.channel.pause()
                self.playing = False
        else:
            # Resume playing
            if self.playing == False:
                self.channel.unpause()
                self.playing = True

        # Normalize the distance between 0 and 1
        player_dist = 1 if player_dist == 0 else 1-min(player_dist/self.audible_range, 1)

        # Smooth player distance with a function
        # We probably need to do some function math that goes above 1 earlier, so that the sound doesnt need to get inside the player so that the volume gets to 1
        player_dist = player_dist**(1-player_dist)#0.5

        # Get volume based on the distance
        volume = self.base_volume * player_dist

        # Get stereo volume
        # Player x and y distance
        delta_x = x2 - x1
        delta_y = y2 - y1

        # Get player angle towards the sound source and rotate it via the player direction
        ear_angle = math.radians(85) # Ear angle relative to the forward looking position
        right_ear_angle = (player_angle + ear_angle) % (TWO_PI)
        left_ear_angle = (player_angle - ear_angle) % (TWO_PI)

        atan_delta = math.atan2(delta_y, delta_x)
        right_relative_angle = (atan_delta - right_ear_angle) %(TWO_PI)
        left_relative_angle = (atan_delta - left_ear_angle) %(TWO_PI)

        if surface:
            pygame.draw.line(surface, (0, 255, 0), (player_x, player_y), (player_x + math.cos(right_ear_angle) * 20, player_y + math.sin(right_ear_angle) * 20), 4)
            pygame.draw.line(surface, (0, 255, 0), (player_x, player_y), (player_x + math.cos(left_ear_angle) * 20, player_y + math.sin(left_ear_angle) * 20), 4)

        # After takin the angle which will be a radian value
        # We normalize it to be between 0 and math.pi and math.pi and 0, so there's no cuts in between the values
        # The direct angle to the ear will have a value of math.pi and the value furthest a value of 0
        right_relative_angle = abs(right_relative_angle - math.pi)
        left_relative_angle = abs(left_relative_angle - math.pi)

        # Normalize it to be between 0 and 1
        right_relative_angle = 0 if right_relative_angle == 0 else  right_relative_angle / math.pi
        left_relative_angle = 0 if left_relative_angle == 0 else  left_relative_angle / math.pi

        # The value to the left ear is just gonna be the opposite
        # Not true anymore, only when they are opposites
        #left_relative_angle = 1-right_relative_angle

        # If the player is close enough sounds will be player from both ears
        # It's kinda of hacky, but this will do it for now
        close_dist = max(player_dist - 0.3, 0)

        # Now we take into account the volume and translate these numbers into a volume
        left_volume = (volume*min(left_relative_angle+close_dist, 1))# (volume*left_relative_angle)+
        right_volume = (volume*min(right_relative_angle+close_dist, 1))#(volume*right_relative_angle)

        self.channel.set_volume(left_volume, right_volume)



def main():##
    global sound_x, sound_y, player_angle, player_x, player_y

    running = True
    clock = pygame.time.Clock()

    sounds = [Sound((WIDTH/2, HEIGHT/2), sound1), Sound((200, 300), soft_piano)]

    for sound in sounds:
        sound.play()

    look_at_mouse = True
    while running:
        clock.tick(60)
        window.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_SPACE:
                   look_at_mouse = not look_at_mouse

        #player_angle += math.radians(0.01) % math.pi*2

        # Update sound position
        mx, my = pygame.mouse.get_pos()
        #sound_x, sound_y = mx, my

        for sound in sounds:
            sound.update(window)

        # Player controls
        keys = pygame.key.get_pressed()
        speed = 5
        if keys[pygame.K_w]:
            player_x += math.cos(player_angle) * speed
            player_y += math.sin(player_angle) * speed
        elif keys[pygame.K_s]:
            player_x += math.cos(player_angle) * -speed
            player_y += math.sin(player_angle) * -speed

        if look_at_mouse:
            player_angle = math.atan2(my - player_y, mx - player_x)

        # Draw player
        pygame.draw.circle(window, (255, 0, 0), (player_x, player_y), 16)
        line_start = (player_x, player_y)
        line_end = (player_x + math.cos(player_angle) * 20, player_y + math.sin(player_angle) * 20)
        pygame.draw.line(window, (255, 255, 0), line_start, line_end, 4)

        for sound in sounds:
            sound.draw(window)

        pygame.display.flip()

    pygame.quit()


main()