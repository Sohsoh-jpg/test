import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fragments of Maya")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
DARK_BLUE = (30, 30, 40)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 200)

# Game states
STAGE_FOREST = 1
STAGE_PIANO = 2
VICTORY_SCREEN = 3

# Piano game states
STATE_PIANO = 1      # Free play mode
STATE_LISTENING = 2  # Computer playing sequence
STATE_GUESSING = 3   # Player guessing sequence
STATE_FEEDBACK = 4   # Showing right/wrong feedback

# Load images
try:
    forest_bg = pygame.image.load("C:/Users/USER/Documents/GitHub/FragmentsOfMaya/fragments/scene3.png")
    forest_bg = pygame.transform.scale(forest_bg, (WIDTH, HEIGHT))
    
    # Load character animations
    character_images = {
        'right': [pygame.transform.scale(pygame.image.load(f'pic{i}.gif'), (100, 130)) for i in range(1, 5)],
        'left': [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'pic{i}.gif'), (100, 130)), True, False) for i in range(1, 5)]
    }
except:
    # Fallback if images don't load
    forest_bg = pygame.Surface((WIDTH, HEIGHT))
    forest_bg.fill((50, 150, 50))  # Green background
    
    # Create placeholder character
    character_images = {
        'right': [pygame.Surface((100, 130)) for _ in range(4)],
        'left': [pygame.Surface((100, 130)) for _ in range(4)]
    }
    for i in range(4):
        character_images['right'][i].fill((200, 100, 100))
        character_images['left'][i].fill((100, 100, 200))
        # Draw simple stick figure
        pygame.draw.circle(character_images['right'][i], BLACK, (50, 30), 15)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 45), (50, 90), 3)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 60), (80, 40), 3)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 60), (20, 40), 3)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 90), (80, 120), 3)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 90), (20, 120), 3)
        
        # Mirror for left-facing
        character_images['left'][i].blit(character_images['right'][i], (0, 0))

# Piano keys configuration
piano_notes = [
    {'key': K_a, 'name': 'A', 'color': (255, 100, 100), 'sound': None},
    {'key': K_b, 'name': 'B', 'color': (255, 180, 100), 'sound': None},
    {'key': K_c, 'name': 'C', 'color': (255, 255, 100), 'sound': None},
    {'key': K_d, 'name': 'D', 'color': (100, 255, 100), 'sound': None},
    {'key': K_e, 'name': 'E', 'color': (100, 255, 255), 'sound': None},
    {'key': K_f, 'name': 'F', 'color': (100, 100, 255), 'sound': None},
    {'key': K_g, 'name': 'G', 'color': (200, 100, 255), 'sound': None}
]

# Load sounds
for note in piano_notes:
    try:
        note['sound'] = pygame.mixer.Sound(f"piano notes/{note['name']}3.mp3")
    except:
        print(f"Couldn't load sound for {note['name']}")
        # Create placeholder beep
        arr = pygame.sndarray.array(note['sound']) if note['sound'] else None
        if arr is not None:
            arr[:] = 0
            note['sound'] = pygame.mixer.Sound(buffer=arr)

key_to_note = {note['key']: note for note in piano_notes}

class GameState:
    def __init__(self):
        # Stage management
        self.current_stage = 1
        self.max_stages = 5
        self.current_phase = 1
        self.max_phases = 5
        self.stage_state = STAGE_FOREST
        
        # Forest variables
        self.x = 250
        self.y = 630
        self.y_velocity = 0
        self.is_jumping = False
        self.current_img = 0
        self.last_switch = 0
        self.direction = 'right'
        self.show_message = False
        
        # Piano variables
        self.piano_state = STATE_PIANO
        self.current_sequence = []
        self.player_sequence = []
        self.feedback_time = 0
        self.sequence_length = 3 + self.current_stage
        self.active_key = None
        self.generate_sequence()
        self.sequence_playing = False
        self.current_note_index = 0
        self.note_time = 0
        self.last_wrong_key = None
        self.wrong_key_time = 0
        self.replay_cooldown = 0
        
        # Victory screen
        self.victory_time = 0

    def generate_sequence(self):
        self.sequence_length = 3 + self.current_stage
        available_notes = [note['name'] for note in piano_notes]
        self.current_sequence = random.sample(available_notes, min(len(available_notes), self.sequence_length))
        self.player_sequence = []
        self.current_note_index = 0

state = GameState()
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 120)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

def play_note(note_name):
    for note in piano_notes:
        if note['name'] == note_name and note['sound']:
            note['sound'].play()
            return note['key']
    return None

def play_sequence():
    state.sequence_playing = True
    state.current_note_index = 0
    state.note_time = pygame.time.get_ticks()

def handle_forest_events(event):
    if event.type == KEYDOWN:
        if event.key == K_SPACE and not state.is_jumping:
            state.is_jumping = True
            state.y_velocity = -15
        elif event.key == K_x and state.show_message:
            state.stage_state = STAGE_PIANO

def handle_piano_events(event):
    if event.type == KEYDOWN:
        if event.key == K_ESCAPE:
            state.stage_state = STAGE_FOREST
            state.x, state.y = 250, 630
        elif event.key == K_RETURN:
            if state.piano_state == STATE_PIANO:
                play_sequence()
                state.piano_state = STATE_LISTENING
            elif state.piano_state == STATE_GUESSING and len(state.player_sequence) == len(state.current_sequence):
                state.piano_state = STATE_FEEDBACK
                state.feedback_time = pygame.time.get_ticks()
        elif event.key == K_BACKSPACE and state.piano_state == STATE_GUESSING:
            if state.player_sequence:
                state.player_sequence.pop()
        elif event.key == K_r and state.piano_state == STATE_GUESSING and pygame.time.get_ticks() - state.replay_cooldown > 1000:
            play_sequence()
            state.piano_state = STATE_LISTENING
            state.replay_cooldown = pygame.time.get_ticks()
        elif event.key in key_to_note and state.piano_state != STATE_FEEDBACK:
            note = key_to_note[event.key]
            if note['sound']:
                note['sound'].play()
            state.active_key = event.key
            if state.piano_state == STATE_GUESSING:
                state.player_sequence.append(note['name'])
                if len(state.player_sequence) <= len(state.current_sequence):
                    if note['name'] != state.current_sequence[len(state.player_sequence)-1]:
                        state.last_wrong_key = event.key
                        state.wrong_key_time = pygame.time.get_ticks()
    
    if event.type == KEYUP and event.key in key_to_note:
        state.active_key = None

def update_forest():
    keys = pygame.key.get_pressed()
    
    if keys[K_LEFT] or keys[K_a]:
        state.x -= 5
        state.direction = 'left'
    elif keys[K_RIGHT] or keys[K_d]:
        state.x += 5
        state.direction = 'right'
    
    if (keys[K_LEFT] or keys[K_RIGHT] or keys[K_a] or keys[K_d]):
        if pygame.time.get_ticks() - state.last_switch > 300:
            state.current_img = (state.current_img + 1) % 4
            state.last_switch = pygame.time.get_ticks()
    
    if state.is_jumping:
        state.y += state.y_velocity
        state.y_velocity += 0.8
        if state.y >= 630:
            state.y = 630
            state.is_jumping = False
    
    state.show_message = (state.x >= 550 and state.x <= 650) and (state.y >= 580 and state.y <= 680)
    state.x = max(-100, min(WIDTH, state.x))

def update_piano():
    current_time = pygame.time.get_ticks()
    
    if state.piano_state == STATE_LISTENING and state.sequence_playing:
        if current_time - state.note_time > 500:
            if state.current_note_index < len(state.current_sequence):
                play_note(state.current_sequence[state.current_note_index])
                state.current_note_index += 1
                state.note_time = current_time
            else:
                state.sequence_playing = False
                if state.piano_state == STATE_LISTENING:
                    state.piano_state = STATE_GUESSING
    
    elif state.piano_state == STATE_FEEDBACK:
        if current_time - state.feedback_time > 2000:
            if state.player_sequence == state.current_sequence:
                state.current_phase += 1
                
                if state.current_phase > state.max_phases:
                    state.current_phase = 1
                    if state.current_stage < state.max_stages:
                        state.current_stage += 1
                    else:
                        state.stage_state = VICTORY_SCREEN
                        state.victory_time = current_time
                
                state.generate_sequence()
                state.piano_state = STATE_PIANO
            else:
                state.generate_sequence()
                state.piano_state = STATE_PIANO
    
    if state.last_wrong_key and current_time - state.wrong_key_time > 500:
        state.last_wrong_key = None

def update_victory():
    current_time = pygame.time.get_ticks()
    if current_time - state.victory_time > 5000:
        state.current_stage = 1
        state.current_phase = 1
        state.stage_state = STAGE_FOREST
        state.x, state.y = 250, 630
        state.generate_sequence()

def render_forest():
    screen.blit(forest_bg, (0, 0))
    screen.blit(character_images[state.direction][state.current_img], (state.x, state.y))
    
    if state.show_message:
        text = font_small.render("Press X for piano challenge", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        screen.blit(text, text_rect)
    
    if state.current_stage > 1:
        stage_text = font_medium.render(f"Stage {state.current_stage}", True, WHITE)
        screen.blit(stage_text, (20, 20))

def render_piano():
    screen.fill(DARK_BLUE)
    
    key_width = WIDTH // 7
    for i, note in enumerate(piano_notes):
        color = note['color']
        if state.active_key == note['key']:
            color = (min(255, color[0] + 100), min(255, color[1] + 100), min(255, color[2] + 100))
        if state.last_wrong_key == note['key']:
            color = RED
        
        pygame.draw.rect(screen, color, (i * key_width, HEIGHT - 200, key_width - 5, 190))
        text = font_medium.render(note['name'], True, BLACK)
        screen.blit(text, (i * key_width + key_width//2 - 10, HEIGHT - 100))
    
    if state.piano_state == STATE_PIANO:
        text = font_medium.render(f"Stage {state.current_stage} - Phase {state.current_phase}/{state.max_phases}", True, WHITE)
        screen.blit(text, (WIDTH//2 - 150, 20))
        
        text = font_medium.render("Press ENTER to start", True, WHITE)
        screen.blit(text, (WIDTH//2 - 120, 70))
        
        text = font_small.render(f"Notes: {state.sequence_length}", True, WHITE)
        screen.blit(text, (WIDTH//2 - 60, 120))
    
    elif state.piano_state == STATE_LISTENING:
        text = font_medium.render("Listen carefully...", True, WHITE)
        screen.blit(text, (WIDTH//2 - 120, 50))
    
    elif state.piano_state == STATE_GUESSING:
        text = font_medium.render(f"Phase {state.current_phase}/{state.max_phases}", True, WHITE)
        screen.blit(text, (WIDTH//2 - 80, 20))
        
        text = font_medium.render("Repeat the sequence:", True, WHITE)
        screen.blit(text, (WIDTH//2 - 140, 70))
        
        for i in range(len(state.current_sequence)):
            color = WHITE if i >= len(state.player_sequence) else (
                GREEN if state.player_sequence[i] == state.current_sequence[i] else RED)
            pygame.draw.circle(screen, color, (WIDTH//2 - 100 + i * 50, 150), 15)
        
        if len(state.player_sequence) == len(state.current_sequence):
            text = font_medium.render("Press ENTER to submit", True, (0, 255, 255))
            screen.blit(text, (WIDTH//2 - 150, 200))
        
        text = font_small.render("R=Replay | BACKSPACE=Undo", True, YELLOW)
        screen.blit(text, (WIDTH//2 - 150, 250))
    
    if state.piano_state == STATE_FEEDBACK:
        if state.player_sequence == state.current_sequence:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(GREEN)
            screen.blit(overlay, (0, 0))
            text = font_large.render("CORRECT!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, text_rect)
            
            if state.current_phase < state.max_phases:
                text = font_medium.render(f"Phase {state.current_phase} completed!", True, WHITE)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
                screen.blit(text, text_rect)
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(RED)
            screen.blit(overlay, (0, 0))
            text = font_large.render("WRONG!", True, WHITE)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, text_rect)
            seq_text = font_medium.render("Sequence: " + "-".join(state.current_sequence), True, WHITE)
            screen.blit(seq_text, (WIDTH//2 - 150, HEIGHT//2 + 100))

def render_victory():
    screen.fill(PURPLE)
    text1 = font_large.render("CONGRATULATIONS!", True, YELLOW)
    text2 = font_medium.render(f"You completed all {state.max_stages} stages!", True, WHITE)
    text3 = font_medium.render(f"Total phases completed: {state.max_stages * state.max_phases}", True, WHITE)
    
    text1_rect = text1.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
    text2_rect = text2.get_rect(center=(WIDTH//2, HEIGHT//2))
    text3_rect = text3.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
    
    screen.blit(text1, text1_rect)
    screen.blit(text2, text2_rect)
    screen.blit(text3, text3_rect)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        
        if state.stage_state == STAGE_FOREST:
            handle_forest_events(event)
        elif state.stage_state == STAGE_PIANO:
            handle_piano_events(event)
        elif state.stage_state == VICTORY_SCREEN and event.type == KEYDOWN:
            state.current_stage = 1
            state.current_phase = 1
            state.stage_state = STAGE_FOREST
            state.x, state.y = 250, 630
            state.generate_sequence()
    

    if state.stage_state == STAGE_FOREST:
        update_forest()
    elif state.stage_state == STAGE_PIANO:
        update_piano()
    elif state.stage_state == VICTORY_SCREEN:
        update_victory()
    
    # Render
    if state.stage_state == STAGE_FOREST:
        render_forest()
    elif state.stage_state == STAGE_PIANO:
        render_piano()
    elif state.stage_state == VICTORY_SCREEN:
        render_victory()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()