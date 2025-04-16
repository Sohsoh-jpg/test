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
STATE_PIANO = 1
STATE_LISTENING = 2
STATE_GUESSING = 3
STATE_FEEDBACK = 4

# Load images
try:
    # Forest background
    forest_bg = pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\scene3.png").convert()
    forest_bg = pygame.transform.scale(forest_bg, (WIDTH, HEIGHT))
    
    # Character animations
    character_images = {
        'right': [pygame.transform.scale(pygame.image.load(f"C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\pic{i}.gif"), (100, 130)) for i in range(1, 5)],
        'left': [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\pic{i}.gif"), (100, 130)), True, False) for i in range(1, 5)]
    }
    
    # Piano images - now with transparency
    piano_bg = pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano.png").convert_alpha()
    piano_bg = pygame.transform.scale(piano_bg, (WIDTH, HEIGHT))
    
    # Make piano keys semi-transparent
    piano_key_bgs = {
        K_a: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano a.png").convert_alpha(),
        K_b: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano b.png").convert_alpha(),
        K_c: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano c.png").convert_alpha(),
        K_d: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano d.png").convert_alpha(),
        K_e: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano e.png").convert_alpha(),
        K_f: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano f.png").convert_alpha(),
        K_g: pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano g.png").convert_alpha()
    }
    
    # Scale key images and set transparency
    for key in piano_key_bgs:
        piano_key_bgs[key] = pygame.transform.scale(piano_key_bgs[key], (WIDTH, HEIGHT))
        piano_key_bgs[key].set_alpha(180)  # Semi-transparent (0-255)

except Exception as e:
    print(f"Error loading images: {e}")
    # Fallback graphics
    forest_bg = pygame.Surface((WIDTH, HEIGHT))
    forest_bg.fill((50, 150, 50))
    
    character_images = {
        'right': [pygame.Surface((100, 130)) for _ in range(4)],
        'left': [pygame.Surface((100, 130)) for _ in range(4)]
    }
    for i in range(4):
        character_images['right'][i].fill((200, 100, 100))
        pygame.draw.circle(character_images['right'][i], BLACK, (50, 30), 15)
        pygame.draw.line(character_images['right'][i], BLACK, (50, 45), (50, 90), 3)
        character_images['left'][i].blit(pygame.transform.flip(character_images['right'][i], True, False), (0, 0))
    
    piano_bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    piano_bg.fill((30, 30, 40, 180))  # Semi-transparent
    piano_key_bgs = {key: pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA) for key in [K_a, K_b, K_c, K_d, K_e, K_f, K_g]}
    for key in piano_key_bgs:
        piano_key_bgs[key].fill((random.randint(50, 200), random.randint(50, 200), random.randint(50, 200), 180))

# Piano configuration
piano_notes = [
    {'key': K_a, 'name': 'A', 'sound': None},
    {'key': K_b, 'name': 'B', 'sound': None},
    {'key': K_c, 'name': 'C', 'sound': None},
    {'key': K_d, 'name': 'D', 'sound': None},
    {'key': K_e, 'name': 'E', 'sound': None},
    {'key': K_f, 'name': 'F', 'sound': None},
    {'key': K_g, 'name': 'G', 'sound': None}
]

# Load sounds
try:
    sound_files = ['A3.mp3', 'B3.mp3', 'C3.mp3', 'D3.mp3', 'E3.mp3', 'F3.mp3', 'G3.mp3']
    for i, note in enumerate(piano_notes):
        note['sound'] = pygame.mixer.Sound(f"C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\piano notes\\{sound_files[i]}")
except Exception as e:
    print(f"Error loading sounds: {e}")
    for note in piano_notes:
        note['sound'] = pygame.mixer.Sound(buffer=bytearray(100))

class GameState:
    def __init__(self):
        self.current_stage = 1
        self.max_stages = 1
        self.current_phase = 1
        self.max_phases = 5
        self.stage_state = STAGE_FOREST
        
        # Forest
        self.x, self.y = 250, 630
        self.y_velocity = 0
        self.is_jumping = False
        self.current_img = 0
        self.last_switch = 0
        self.direction = 'right'
        self.show_message = False
        
        # Piano
        self.piano_state = STATE_PIANO
        self.current_sequence = []
        self.player_sequence = []
        self.active_key = None
        self.generate_sequence()
        self.sequence_playing = False
        self.current_note_index = 0
        self.note_time = 0
        self.last_wrong_key = None
        self.wrong_key_time = 0
        self.replay_cooldown = 0
        self.key_pressed_time = 0
        self.feedback_time = 0
        self.show_visual_keys = True  # Controls whether to show key highlights
        
        # Victory
        self.victory_time = 0

    def generate_sequence(self):
        self.sequence_length = 3 + self.current_stage
        self.current_sequence = random.sample([note['name'] for note in piano_notes], min(7, self.sequence_length))
        self.player_sequence = []
        self.current_note_index = 0

state = GameState()
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 120)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

def play_note(note_name, show_visual=True):
    """Play a note sound and optionally show the key press visually"""
    for note in piano_notes:
        if note['name'] == note_name and note['sound']:
            note['sound'].play()
            if show_visual:
                state.active_key = note['key']
                state.key_pressed_time = pygame.time.get_ticks()
            return note['key']
    return None

def play_sequence():
    """Start playing the sequence of notes"""
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
        elif event.key in {note['key'] for note in piano_notes} and state.piano_state != STATE_FEEDBACK:
            note = next(n for n in piano_notes if n['key'] == event.key)
            note['sound'].play()
            state.active_key = event.key
            state.key_pressed_time = pygame.time.get_ticks()
            if state.piano_state == STATE_GUESSING:
                state.player_sequence.append(note['name'])
                if len(state.player_sequence) <= len(state.current_sequence):
                    if note['name'] != state.current_sequence[len(state.player_sequence)-1]:
                        state.last_wrong_key = event.key
                        state.wrong_key_time = pygame.time.get_ticks()
    
    if event.type == KEYUP and event.key in {note['key'] for note in piano_notes}:
        if state.active_key == event.key:
            state.active_key = None

def update_forest():
    keys = pygame.key.get_pressed()
    
    if keys[K_LEFT] or keys[K_a]:
        state.x = max(-100, state.x - 5)
        state.direction = 'left'
    elif keys[K_RIGHT] or keys[K_d]:
        state.x = min(WIDTH, state.x + 5)
        state.direction = 'right'
    
    if (keys[K_LEFT] or keys[K_RIGHT] or keys[K_a] or keys[K_d]) and pygame.time.get_ticks() - state.last_switch > 300:
        state.current_img = (state.current_img + 1) % 4
        state.last_switch = pygame.time.get_ticks()
    
    if state.is_jumping:
        state.y += state.y_velocity
        state.y_velocity += 0.8
        if state.y >= 630:
            state.y = 630
            state.is_jumping = False
    
    state.show_message = (550 <= state.x <= 650) and (580 <= state.y <= 680)

def update_piano():
    current_time = pygame.time.get_ticks()
    
    if state.piano_state == STATE_LISTENING and state.sequence_playing:
        if current_time - state.note_time > 500:
            if state.current_note_index < len(state.current_sequence):
                # Play the note sound but DON'T show the key visually
                play_note(state.current_sequence[state.current_note_index], show_visual=False)
                state.current_note_index += 1
                state.note_time = current_time
            else:
                state.sequence_playing = False
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
    
    if state.last_wrong_key and current_time - state.wrong_key_time > 500:
        state.last_wrong_key = None
    if state.active_key and current_time - state.key_pressed_time > 500:
        state.active_key = None

def update_victory():
    if pygame.time.get_ticks() - state.victory_time > 5000:
        state.current_stage = 1
        state.current_phase = 1
        state.stage_state = STAGE_FOREST
        state.x, state.y = 250, 630

def render_forest():
    screen.blit(forest_bg, (0, 0))
    screen.blit(character_images[state.direction][state.current_img], (state.x, state.y))
    
    if state.show_message:
        text = font_small.render("Press X for piano challenge", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 50))
    
    if state.current_stage > 1:
        text = font_medium.render(f"Stage {state.current_stage}", True, WHITE)
        screen.blit(text, (20, 20))

def render_piano():
    # 1. Draw forest background first (shows through transparency)
    screen.blit(forest_bg, (0, 0))
    
    # 2. Draw piano background with proper transparency
    screen.blit(piano_bg, (0, 0))
    
    # 3. Add semi-transparent overlay for better UI visibility
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((30, 30, 40, 120))  # Semi-transparent dark blue
    screen.blit(overlay, (0, 0))
    
    # 4. Draw active piano key when pressed (only during player's turn, not during listening)
    if state.piano_state != STATE_LISTENING and state.active_key and pygame.time.get_ticks() - state.key_pressed_time < 500:
        screen.blit(piano_key_bgs[state.active_key], (0, 0))
    
    # 5. UI Elements (non-transparent)
    if state.piano_state == STATE_PIANO:
        texts = [
            f"Stage {state.current_stage} - Phase {state.current_phase}/{state.max_phases}",
            "Press ENTER to start",
            f"Notes: {state.sequence_length}"
        ]
        for i, text in enumerate(texts):
            rendered = font_medium.render(text, True, WHITE)
            screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, 20 + i * 50))
    
    elif state.piano_state == STATE_LISTENING:
        text = font_medium.render("Listen carefully...", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 50))
    
    elif state.piano_state == STATE_GUESSING:
        # Progress dots
        for i in range(len(state.current_sequence)):
            color = WHITE if i >= len(state.player_sequence) else (
                GREEN if state.player_sequence[i] == state.current_sequence[i] else RED)
            pygame.draw.circle(screen, color, (WIDTH//2 - 100 + i * 50, 150), 15)
        
        texts = [
            f"Phase {state.current_phase}/{state.max_phases}",
            "Repeat the sequence:",
            "R=Replay | BACKSPACE=Undo"
        ]
        for i, text in enumerate(texts):
            rendered = font_medium.render(text, True, WHITE) if i != 2 else font_small.render(text, True, YELLOW)
            screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, 20 + i * 70))
        
        if len(state.player_sequence) == len(state.current_sequence):
            text = font_medium.render("Press ENTER to submit", True, (0, 255, 255))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 200))
    
    elif state.piano_state == STATE_FEEDBACK:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 255, 0, 180) if state.player_sequence == state.current_sequence else (255, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        text = font_large.render("CORRECT!" if state.player_sequence == state.current_sequence else "WRONG!", True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 50))
        
        if state.player_sequence != state.current_sequence:
            text = font_medium.render(f"Sequence: {'-'.join(state.current_sequence)}", True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 50))

def render_victory():
    try:
        # Load victory background with corrected path
        victory_bg = pygame.image.load("C:\\Users\\USER\\Documents\\GitHub\\FragmentsOfMaya\\fragments\\mysterybg.png").convert()
        victory_bg = pygame.transform.scale(victory_bg, (WIDTH, HEIGHT))
        screen.blit(victory_bg, (0, 0))
    except Exception as e:
        print(f"Error loading victory background: {e}")
        # Fallback for victory screen
        screen.fill(PURPLE)  # Fallback to purple if image can't be loaded
    
    texts = [
        "CONGRATULATIONS!",
        f"You completed all the piano stage!",
        f"But don't get too excited, this is just the beginning."
    ]
    for i, text in enumerate(texts):
        rendered = font_large.render(text, True, YELLOW) if i == 0 else font_medium.render(text, True, WHITE)
        screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, HEIGHT//2 - 100 + i * 100))

# Main loop
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
    
    # Update
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