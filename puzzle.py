import pygame
import random
import math
import os
import sys

# Initialize pygame
pygame.init()
screen_width, screen_height = 800, 650
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Maya's Memories: The Fragmented Self")
clock = pygame.time.Clock()

# Game Constants
GRID_COLS = 4  # Changed to 4 columns for better layout
GRID_ROWS = 3  # Changed to 3 rows
CARD_WIDTH, CARD_HEIGHT = 160, 160  # Slightly smaller cards to fit grid
MARGIN = 20
LIVES = 3

# Colors
BG_COLOR = (15, 5, 25)
CARD_BACK_COLOR = (30, 20, 40)
GOOD_GLOW = (100, 200, 100, 50)
BAD_GLOW = (200, 100, 100, 50)
TRAUMA_FLASH = (150, 0, 0, 50)
POSITIVE_FLASH = (100, 200, 150, 50)

# Custom events
CARD_FLIP_BACK_EVENT = pygame.USEREVENT + 1
MESSAGE_FADE_EVENT = pygame.USEREVENT + 2
GAME_EXIT_EVENT = pygame.USEREVENT + 3

class Card:
    def __init__(self, card_type, image_key):
        self.type = card_type  # "good" or "bad"
        self.image_key = image_key
        self.matched = False
        self.selected = False
        self.x = 0
        self.y = 0
        self.pulse_offset = random.random() * 10

def load_image(path, size=(CARD_WIDTH, CARD_HEIGHT)):
    try:
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Path does not exist: {abs_path}")
        image = pygame.image.load(abs_path)
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image {path}: {e}")
        placeholder = pygame.Surface(size)
        color = (random.randint(50, 100), random.randint(50, 100), random.randint(50, 100))
        placeholder.fill(color)
        return placeholder

def create_card_back():
    surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT), pygame.SRCALPHA)
    surface.fill((*CARD_BACK_COLOR, 200))
    for _ in range(15):
        pos = (random.randint(5, CARD_WIDTH-5), random.randint(5, CARD_HEIGHT-5))
        radius = random.randint(1, 3)
        color = (random.randint(50, 70), random.randint(30, 50), random.randint(70, 90), 100)
        pygame.draw.circle(surface, color, pos, radius)
    return surface

class Game:
    def __init__(self):
        self.load_assets()
        self.reset_game()
        
    def load_assets(self):
        self.card_back = create_card_back()
        # Get the current file's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        stage2_dir = os.path.join(base_dir, "stage2")
        
        # Create stage2 directory if it doesn't exist
        if not os.path.exists(stage2_dir):
            os.makedirs(stage2_dir)
            print(f"Created directory: {stage2_dir}")
        
        # Define empty placeholders for images that might not load
        self.images = {}
        
        # Try to load images or create placeholders
        image_paths = {
            # Good memories
            "flower": os.path.join(stage2_dir, "flower.png"),
            "diploma": os.path.join(stage2_dir, "diploma.jpg"),
            "handshake": os.path.join(stage2_dir, "handshake.png"),
            # Bad memories
            "evil": os.path.join(stage2_dir, "evil.jpg"),
            "crying": os.path.join(stage2_dir, "crying.webp"),
            "death": os.path.join(stage2_dir, "death.png")
        }
        
        # Load images or create colored placeholders
        colors = {
            "flower": (100, 200, 100),      # Green for flower
            "diploma": (200, 200, 100),     # Yellow for diploma
            "handshake": (100, 150, 200),   # Blue for handshake
            "evil": (200, 50, 50),          # Red for evil
            "crying": (150, 100, 200),      # Purple for crying
            "death": (100, 100, 100)        # Gray for death
        }
        
        for key, path in image_paths.items():
            try:
                self.images[key] = load_image(path)
                print(f"Loaded image: {key}")
            except Exception as e:
                print(f"Creating placeholder for {key}: {e}")
                # Create a colored placeholder with text
                placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
                placeholder.fill(colors[key])
                font = pygame.font.SysFont("Arial", 20)
                text = font.render(key, True, (255, 255, 255))
                placeholder.blit(text, (CARD_WIDTH//2 - text.get_width()//2, CARD_HEIGHT//2 - text.get_height()//2))
                self.images[key] = placeholder
        
        try:
            bg_path = os.path.join(stage2_dir, "mysterybg.png")
            if os.path.exists(bg_path):
                self.background = pygame.image.load(bg_path)
                self.background = pygame.transform.scale(self.background, (screen_width, screen_height))
            else:
                raise FileNotFoundError(f"Background image not found at {bg_path}")
        except Exception as e:
            print(f"Error loading background: {e}")
            self.background = pygame.Surface((screen_width, screen_height))
            self.background.fill(BG_COLOR)
            
            # Add some visual elements to the background
            for _ in range(50):
                x = random.randint(0, screen_width)
                y = random.randint(0, screen_height)
                radius = random.randint(1, 3)
                color = (random.randint(30, 50), random.randint(20, 40), random.randint(40, 60))
                pygame.draw.circle(self.background, color, (x, y), radius)
    
    def reset_game(self):
        self.cards = []
        self.selected_indices = []
        self.matched_good_pairs = 0
        self.matched_bad_pairs = 0
        self.lives = LIVES
        self.game_over = False
        self.win = False
        self.pulse_time = 0
        self.trauma_alpha = 0
        self.positive_alpha = 0
        self.can_select = True
        self.message = ""
        self.message_alpha = 0
        self.message_size = 36
        self.message_color = (255, 80, 80)
        self.is_positive_message = False
        self.win_display_time = 0
        
        # Negative messages when getting wrong matches
        self.negative_messages = [
            "You are unworthy of love",
            "I hate you",
            "You are miserable",
            "You will never succeed",
            "No one cares about you",
            "Everything is your fault",
            "You're a disappointment",
            "Give up now"
        ]
        
        # Positive messages when matching good pairs
        self.positive_messages = [
            "You are worthy of love",
            "You are beautiful",
            "You can achieve anything",
            "You are strong and brave",
            "People appreciate you",
            "You bring joy to others",
            "You make a difference",
            "Your future is bright",
            "You are enough"
        ]
        
        # Create 3 good pairs and 3 bad pairs
        good_pairs = [
            ("good", "flower"), 
            ("good", "diploma"),
            ("good", "handshake")
        ]
        
        bad_pairs = [
            ("bad", "evil"),
            ("bad", "crying"),
            ("bad", "death")
        ]
        
        # Duplicate each pair and combine
        pairs = []
        for pair in good_pairs:
            pairs.append(pair)
            pairs.append(pair)  # Add each pair twice
            
        for pair in bad_pairs:
            pairs.append(pair)
            pairs.append(pair)  # Add each pair twice
        
        # Shuffle all cards
        random.shuffle(pairs)
        
        # Position cards in a 4x3 grid
        for i, (card_type, img_key) in enumerate(pairs):
            card = Card(card_type, img_key)
            row = i // GRID_COLS
            col = i % GRID_COLS
            
            # Calculate x,y position with centered grid
            grid_width = GRID_COLS * (CARD_WIDTH + MARGIN) - MARGIN
            grid_height = GRID_ROWS * (CARD_HEIGHT + MARGIN) - MARGIN
            
            start_x = (screen_width - grid_width) // 2
            start_y = (screen_height - grid_height) // 2 - 25  # Shift up a bit for lives display
            
            card.x = start_x + col * (CARD_WIDTH + MARGIN)
            card.y = start_y + row * (CARD_HEIGHT + MARGIN)
            self.cards.append(card)
    
    def handle_click(self, pos):
        if self.game_over:
            if not self.win:  # Only allow reset if player lost
                self.reset_game()
            return
            
        if not self.can_select:
            return
            
        x, y = pos
        for i, card in enumerate(self.cards):
            if (not card.matched and not card.selected and 
                card.x <= x <= card.x + CARD_WIDTH and 
                card.y <= y <= card.y + CARD_HEIGHT):
                
                card.selected = True
                self.selected_indices.append(i)
                
                if len(self.selected_indices) == 2:
                    self.check_match()
                    self.can_select = False
                    pygame.time.set_timer(CARD_FLIP_BACK_EVENT, 1000)
                break
    
    def check_match(self):
        if len(self.selected_indices) != 2:
            return
            
        card1 = self.cards[self.selected_indices[0]]
        card2 = self.cards[self.selected_indices[1]]
        
        # Check if the cards are the same type and image
        if card1.image_key == card2.image_key:
            card1.matched = True
            card2.matched = True
            
            if card1.type == "good":
                self.matched_good_pairs += 1
                # Show a positive message when matching good pairs
                self.show_positive_message()
                self.positive_alpha = 180
                
                if self.matched_good_pairs == 3:  # All 3 good pairs matched
                    self.win = True
                    self.game_over = True
                    # Set timer to exit game after showing win message
                    pygame.time.set_timer(GAME_EXIT_EVENT, 3000)  # Exit after 3 seconds
            else:  # "bad" type
                self.matched_bad_pairs += 1
                self.lives -= 1
                self.trauma_alpha = 180
                
                # Show a negative message when matching bad pairs
                self.show_negative_message()
                
                if self.lives <= 0:
                    self.game_over = True
        else:
            # Show a negative message for non-matching cards
            self.show_negative_message()
    
    def show_negative_message(self):
        self.message = random.choice(self.negative_messages)
        self.message_alpha = 255
        self.message_size = random.randint(36, 48)  # Random size for variation
        self.message_color = (255, 80, 80)  # Red for negative messages
        self.is_positive_message = False
        pygame.time.set_timer(MESSAGE_FADE_EVENT, 2000)  # Message starts fading after 2 seconds
    
    def show_positive_message(self):
        self.message = random.choice(self.positive_messages)
        self.message_alpha = 255
        self.message_size = random.randint(36, 48)  # Random size for variation
        self.message_color = (100, 255, 150)  # Green for positive messages
        self.is_positive_message = True
        pygame.time.set_timer(MESSAGE_FADE_EVENT, 2000)  # Message starts fading after 2 seconds
    
    def handle_flip_back_timer(self):
        pygame.time.set_timer(CARD_FLIP_BACK_EVENT, 0)
        for i in self.selected_indices:
            if not self.cards[i].matched:
                self.cards[i].selected = False
        self.selected_indices = []
        self.can_select = True
    
    def handle_message_fade(self):
        pygame.time.set_timer(MESSAGE_FADE_EVENT, 0)
    
    def handle_game_exit(self):
        # This is called when the player wins
        pygame.time.set_timer(GAME_EXIT_EVENT, 0)
        pygame.quit()
        sys.exit()
    
    def update(self):
        self.pulse_time += 0.05
        self.trauma_alpha = max(0, self.trauma_alpha - 3)
        self.positive_alpha = max(0, self.positive_alpha - 3)
        
        # Fade out message
        if self.message_alpha > 0:
            self.message_alpha = max(0, self.message_alpha - 2)
    
    def draw(self):
        screen.blit(self.background, (0, 0))
        
        # Draw trauma flash (red overlay) for bad matches
        if self.trauma_alpha > 0:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((*TRAUMA_FLASH[:3], self.trauma_alpha))
            screen.blit(overlay, (0, 0))
            
        # Draw positive flash (green overlay) for good matches
        if self.positive_alpha > 0:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((*POSITIVE_FLASH[:3], self.positive_alpha))
            screen.blit(overlay, (0, 0))
        
        for i, card in enumerate(self.cards):
            pulse = 1 + 0.03 * math.sin(self.pulse_time * 3 + card.pulse_offset)
            
            if card.matched or card.selected:
                glow_color = GOOD_GLOW if card.type == "good" else BAD_GLOW
                glow = pygame.Surface((CARD_WIDTH+20, CARD_HEIGHT+20), pygame.SRCALPHA)
                pygame.draw.rect(glow, glow_color, (0, 0, CARD_WIDTH+20, CARD_HEIGHT+20), border_radius=10)
                screen.blit(glow, (card.x-10, card.y-10))
                screen.blit(self.images[card.image_key], (card.x, card.y))
            else:
                scaled_back = pygame.transform.scale(
                    self.card_back,
                    (int(CARD_WIDTH * pulse), int(CARD_HEIGHT * pulse))
                )
                screen.blit(scaled_back, 
                    (card.x + (CARD_WIDTH - CARD_WIDTH*pulse)/2,
                     card.y + (CARD_HEIGHT - CARD_HEIGHT*pulse)/2))
        
        # Draw lives
        for i in range(self.lives):
            pos = (screen_width - 30 - i * 40, screen_height - 30)
            pygame.draw.circle(screen, (200, 50, 50), pos, 15)
        
        # Draw messages (positive or negative)
        if self.message and self.message_alpha > 0:
            font = pygame.font.SysFont("Arial", self.message_size, bold=True)
            text = font.render(self.message, True, (*self.message_color, self.message_alpha))
            
            # Add shake effect for negative messages, smooth movement for positive ones
            if self.is_positive_message:
                # Gentle floating effect for positive messages
                offset_y = 5 * math.sin(self.pulse_time * 2)
                shake_x = 0
                shake_y = int(offset_y)
            else:
                # Random shake for negative messages
                shake_x = random.randint(-3, 3) if self.message_alpha > 200 else 0
                shake_y = random.randint(-3, 3) if self.message_alpha > 200 else 0
            
            pos_x = screen_width//2 - text.get_width()//2 + shake_x
            pos_y = screen_height//2 - 150 + shake_y  # Above the cards
            
            text_surface = pygame.Surface((text.get_width(), text.get_height()), pygame.SRCALPHA)
            text_surface.blit(text, (0, 0))
            
            screen.blit(text_surface, (pos_x, pos_y))
        
        if self.game_over:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            if self.win:
                msg = "Love is within you, remember that..."
                color = (150, 255, 150)
                
                font = pygame.font.SysFont("Arial", 48)
                text = font.render(msg, True, color)
                screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - 30))
                
                # No "try again" text for win condition
                # The game will automatically close after the timer expires
            else:
                msg = "Hateress overtakes you, try again."
                color = (255, 100, 100)
                
                font = pygame.font.SysFont("Arial", 48)
                text = font.render(msg, True, color)
                screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - 30))
                
                # Only show "click to try again" for loss condition
                subtext = pygame.font.SysFont("Arial", 24).render("Click to try again", True, (200, 200, 200))
                screen.blit(subtext, (screen_width//2 - subtext.get_width()//2, screen_height//2 + 30))

def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
            elif event.type == CARD_FLIP_BACK_EVENT:
                game.handle_flip_back_timer()
            elif event.type == MESSAGE_FADE_EVENT:
                game.handle_message_fade()
            elif event.type == GAME_EXIT_EVENT:
                game.handle_game_exit()
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()