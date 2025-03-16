import pygame

pygame.init()

WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Load images
background = pygame.image.load('C:/Users/USER/Documents/Python/fragments/forest.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

picture1 = pygame.image.load('C:/Users/USER/Pictures/pic1.gif')
picture1 = pygame.transform.scale(picture1, (100, 130))
picture1_flipped = pygame.transform.flip(picture1, True, False)

picture2 = pygame.image.load('C:/Users/USER/Pictures/pic2.gif')
picture2 = pygame.transform.scale(picture2, (100, 130))
picture2_flipped = pygame.transform.flip(picture2, True, False)

picture3 = pygame.image.load('C:/Users/USER/Pictures/pic3.gif')
picture3 = pygame.transform.scale(picture3, (100, 130))
picture3_flipped = pygame.transform.flip(picture3, True, False)

picture4 = pygame.image.load('C:/Users/USER/Pictures/pic4.gif')
picture4 = pygame.transform.scale(picture4, (100, 130))
picture4_flipped = pygame.transform.flip(picture4, True, False)

# Initial positions
x_pos = 250
y_pos = 630
original_y_pos = y_pos

# Stage trigger position
trigger_x = 600  # X position to trigger stage change
trigger_y = 630  # Y position to trigger stage change

# Stage variables
current_stage = 1
stage_changed = False

clock = pygame.time.Clock()

last_switch_time = pygame.time.get_ticks()
current_image = picture1
image_flipped = False

is_jumping = False
jump_speed = 10
gravity = 0.5
y_velocity = 0

# Font for the message
font = pygame.font.Font(None, 36)

finish = False
while not finish:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finish = True

    keys = pygame.key.get_pressed()

    # Movement logic (unchanged)
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        x_pos += 5
        if image_flipped:
            current_image = pygame.transform.flip(current_image, True, False)
            image_flipped = False
            current_image = picture1

        current_time = pygame.time.get_ticks()
        if current_time - last_switch_time >= 300:
            if current_image == picture1:
                current_image = picture2
            elif current_image == picture2:
                current_image = picture3
            elif current_image == picture3:
                current_image = picture4
            else:
                current_image = picture1

            last_switch_time = current_time

    elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
        x_pos -= 5
        if not image_flipped:
            current_image = pygame.transform.flip(current_image, True, False)
            image_flipped = True
            current_image = picture1_flipped

        current_time = pygame.time.get_ticks()
        if current_time - last_switch_time >= 300:
            if current_image == picture1_flipped:
                current_image = picture2_flipped
            elif current_image == picture2_flipped:
                current_image = picture3_flipped
            elif current_image == picture3_flipped:
                current_image = picture4_flipped
            else:
                current_image = picture1_flipped

            last_switch_time = current_time

    if keys[pygame.K_SPACE] and not is_jumping:
        is_jumping = True
        y_velocity = -jump_speed

    if is_jumping:
        y_pos += y_velocity
        y_velocity += gravity

        if y_pos >= original_y_pos:
            y_pos = original_y_pos
            is_jumping = False
            y_velocity = 0

    if x_pos > WIDTH:
        x_pos = -current_image.get_width()
    elif x_pos < -current_image.get_width():
        x_pos = WIDTH

    # Check if character is at the trigger position
    show_message = False
    if (x_pos >= trigger_x - 50 and x_pos <= trigger_x + 50) and (y_pos >= trigger_y - 50 and y_pos <= trigger_y + 50):
        show_message = True  # Set flag to show the message

        # Check if X key is pressed
        if keys[pygame.K_x]:
            current_stage += 1
            stage_changed = True

    # Reset the screen for the new stage
    if stage_changed:
        if current_stage == 2:
            # Load new background for stage 2
            background = pygame.image.load('C:/Users/USER/Documents/Python/fragments/piano.png')
            background = pygame.transform.scale(background, (WIDTH, HEIGHT))
            # Reset character position
            x_pos = 100
            y_pos = 100
            # Reset other variables if needed
            stage_changed = False

    # Draw the screen
    screen.blit(background, (0, 0))  # Draw the background first
    screen.blit(current_image, (x_pos, y_pos))  # Draw the character

    # Draw the message if the character is in the trigger area
    if show_message:
        text = font.render("Press X to enter the next stage", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 50))  # Center the text
        screen.blit(text, text_rect)  # Draw the message

    pygame.display.flip()

    clock.tick(60)

pygame.quit()