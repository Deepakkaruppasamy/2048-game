import pygame
import random
import sys
import sqlite3
import bcrypt
import time


SIZE = 5
TILE_SIZE = 100
PADDING = 10
WINDOW_WIDTH = SIZE * TILE_SIZE + 800
WINDOW_HEIGHT = SIZE * TILE_SIZE + 150
ANIMATION_SPEED = 150

BACKGROUND_COLOR = (250, 248, 239)
TILE_COLOR = {
    0: (204, 192, 179),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}
TEXT_COLOR = {0: (119, 110, 101), 2: (119, 110, 101), 4: (119, 110, 101), 8: (255, 255, 255)}

pygame.font.init()
FONT_MAIN = pygame.font.Font(pygame.font.get_default_font(), 40)
FONT_SCORE = pygame.font.Font(pygame.font.get_default_font(), 24)
FONT_INPUT = pygame.font.Font(pygame.font.get_default_font(), 28)
DB_NAME = 'high_scores.db'

def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, high_score INTEGER)''')
    conn.commit()
    conn.close()

def signup(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password, high_score) VALUES (?, ?, ?)", (username, hashed_password, 0))
        conn.commit()
        return True, "Signup successful!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose a different username."
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result and bcrypt.checkpw(password.encode(), result[0]):
        return True, "Login successful!"
    else:
        return False, "Invalid username or password."

def get_high_score(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT high_score FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def save_high_score(username, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET high_score = ? WHERE username = ? AND high_score < ?", (score, username, score))
    conn.commit()
    conn.close()

def start_game():
    mat = [[0] * SIZE for _ in range(SIZE)]
    add_new(mat)
    add_new(mat)
    return mat

def add_new(mat):
    empty_cells = [(i, j) for i in range(SIZE) for j in range(SIZE) if mat[i][j] == 0]
    if empty_cells:
        i, j = random.choice(empty_cells)
        mat[i][j] = random.choice([2, 4])

def draw_text(window, text, position, font, color):
    text_surface = font.render(text, True, color)
    window.blit(text_surface, position)


def draw_input_box(win, text, rect, active):
    color = (0, 0, 0) if active else (150, 150, 150)
    pygame.draw.rect(win, color, rect, 2)
    draw_text(win, text, (rect.x + 5, rect.y + 5), FONT_SCORE, (0, 0, 0))

def main_menu_screen(win):
    running = True
    selected_option = None
    button_color = (100, 100, 250)
    button_hover_color = (50, 50, 200)

    while running:
        win.fill((240, 230, 200))
        draw_text(win, "2048 Deep Version", (win.get_width() // 2 - 120, 80), FONT_MAIN, (102, 51, 0))

        # Buttons
        buttons = [
            {"label": "Start Game", "rect": pygame.Rect(win.get_width() // 2 - 100, 200, 200, 50)},
            {"label": "About", "rect": pygame.Rect(win.get_width() // 2 - 100, 280, 200, 50)},
            {"label": "Exit", "rect": pygame.Rect(win.get_width() // 2 - 100, 360, 200, 50)},
        ]

        # Draw Buttons
        for button in buttons:
            color = button_hover_color if button["rect"].collidepoint(pygame.mouse.get_pos()) else button_color
            pygame.draw.rect(win, color, button["rect"], border_radius=8)
            draw_text(win, button["label"], (button["rect"].x + 50, button["rect"].y + 10), FONT_SCORE, (255, 255, 255))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if buttons[0]["rect"].collidepoint(event.pos):
                    selected_option = "start"
                    running = False
                elif buttons[1]["rect"].collidepoint(event.pos):
                    selected_option = "about"
                    running = False
                elif buttons[2]["rect"].collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

    return selected_option

def draw_text(win, text, pos, font, color=(0, 0, 0)):
    text_surface = font.render(text, True, color)
    win.blit(text_surface, pos)
def display_error_message(win, message):
    # Define the text color for error message
    text_color = (255, 0, 0)  # Red color
    
    # Render the message text
    error_text = FONT_MAIN.render(message, True, text_color)
    
    # Get the width and height of the text to center it
    text_width = error_text.get_width()
    text_height = error_text.get_height()
    
    # Calculate the position to center the text horizontally at the bottom
    x_position = (win.get_width() - text_width) // 2
    y_position = win.get_height() - text_height - 20  # 20px from the bottom
    
    # Draw the error message on the screen
    win.blit(error_text, (x_position, y_position))




FONT_LABEL = pygame.font.Font(None, 36)
def login_signup_screen(win):
    username = ''
    password = ''
    active_field = "username"
    show_cursor = True
    cursor_timer = time.time()
    is_signup = False  # Flag to toggle between login and signup
    message = ""
    background_image = pygame.image.load('logo5.png')  # Load image file
    image_rect = background_image.get_rect() 
    running = True
    while running:
        win.fill((240, 230, 200))  # Background color
        draw_text(win, "Login / Signup", (win.get_width() // 2 - 90, 50), FONT_MAIN, (102, 51, 0))

        # Labels
        draw_text(win, "Username:", (30, 150), FONT_SCORE, (0, 0, 0))
        draw_text(win, "Password:", (20, 230), FONT_SCORE, (0, 0, 0))

        # Assuming message contains the error message (e.g., "Code exists" or login/signup error message)
        message_width = FONT_SCORE.size(message)[0]  # Get the width of the message

# Calculate the x position to center the text horizontally
        x_position = (win.get_width() - message_width) // 2
        
# Now, you can use this x_position to center the message

        # Username Input Box
        username_rect = pygame.Rect(win.get_width() // 2 - 100, 150, 200, 40)
        pygame.draw.rect(win, (255, 255, 255), username_rect, border_radius=5)
        pygame.draw.rect(win, (0, 0, 0), username_rect, 2, border_radius=5)

        # Password Input Box
        password_rect = pygame.Rect(win.get_width() // 2 - 100, 230, 200, 40)
        pygame.draw.rect(win, (255, 255, 255), password_rect, border_radius=5)
        pygame.draw.rect(win, (0, 0, 0), password_rect, 2, border_radius=5)

        # Blinking cursor effect
        if time.time() - cursor_timer > 0.5:
            show_cursor = not show_cursor
            cursor_timer = time.time()

        # Display Username
        username_display = username + ('|' if show_cursor and active_field == "username" else '')
        draw_text(win, username_display, (username_rect.x + 10, username_rect.y + 5), FONT_INPUT, (0, 0, 0))

        # Display Password (masked with asterisks)
        password_display = '*' * len(password) + ('|' if show_cursor and active_field == "password" else '')
        draw_text(win, password_display, (password_rect.x + 10, password_rect.y + 5), FONT_INPUT, (0, 0, 0))

        # Buttons
        login_signup_button = pygame.Rect(win.get_width() // 2 - 70, 310, 80, 40)
        toggle_button = pygame.Rect(win.get_width() // 2 - 70, 370, 140, 40)

        # Login/Signup button (based on is_signup flag)
        button_label = "Sign" if not is_signup else "Login"
        pygame.draw.rect(win, (100, 150, 250), login_signup_button, border_radius=8)
        pygame.draw.rect(win, (50, 100, 200), toggle_button, border_radius=8)

        draw_text(win, button_label, (login_signup_button.x + 12, login_signup_button.y + 5), FONT_SCORE, (255, 255, 255))
        draw_text(win, "" + ("Signup" if is_signup else "Login"), (toggle_button.x + 10, toggle_button.y + 5), FONT_SCORE, (255, 255, 255))

        pygame.display.flip()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Switch active field based on click location
                if username_rect.collidepoint(event.pos):
                    active_field = "username"
                elif password_rect.collidepoint(event.pos):
                    active_field = "password"
                elif login_signup_button.collidepoint(event.pos):
                    # Call signup if we are on login form, or login if we are on signup form
                    if not is_signup:  # Signup
                        success, message = signup(username, password)
                        if success:
                            return username  # Successful signup, return username
                        else:
                            draw_text(win, message, (x_position, win.get_height() - 50), FONT_SCORE, (255, 0, 0))


                            pygame.display.flip()
                            pygame.time.delay(2000)  # Show error for 2 seconds
                    else:  # Login
                        success, message = login(username, password)
                        if success:
                            return username  # Successful login
                        else:
                            draw_text(win, message, (x_position, win.get_height() - 50), FONT_SCORE, (255, 0, 0))

                            pygame.display.flip()
                            pygame.time.delay(2000)  # Show error for 2 seconds
                elif toggle_button.collidepoint(event.pos):
                    # Switch between login and signup
                    is_signup = not is_signup
                    username = ''
                    password = ''  # Clear fields on switching

            elif event.type == pygame.KEYDOWN:
                if active_field == "username":
                    if event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    else:
                        username += event.unicode
                elif active_field == "password":
                    if event.key == pygame.K_BACKSPACE:
                        password = password[:-1]
                    else:
                        password += event.unicode



def game_info_screen(win):
    running = True
    while running:
        win.fill((240, 230, 200))  
        draw_text(win, "Welcome to 2048 Deep Version!", (50, 50), FONT_MAIN, (102, 51, 0))
        draw_text(win, "Objective: Combine tiles to reach the highest score possible.", (50, 150), FONT_SCORE, (51, 51, 0))
        draw_text(win, "Rules:", (50, 200), FONT_SCORE, (51, 51, 0))
        draw_text(win, "- Use arrow keys to slide tiles.", (70, 250), FONT_SCORE, (51, 51, 0))
        draw_text(win, "- Combine tiles of the same value to increase score.", (70, 280), FONT_SCORE, (51, 51, 0))
        draw_text(win, "- Game over when no moves are left.", (70, 310), FONT_SCORE, (51, 51, 0))
        draw_text(win, "Press Enter to Start the Game!", (50, 400), FONT_SCORE, (204, 0, 0))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return


def swipe_left(mat):
    score = 0
    for i in range(SIZE):
        new_row = [num for num in mat[i] if num != 0]
        new_row, merges = merge_tiles(new_row)
        mat[i] = new_row + [0] * (SIZE - len(new_row))
        score += merges
    return score

def swipe_right(mat):
    score = 0
    for i in range(SIZE):
        new_row = [num for num in mat[i] if num != 0]
        new_row.reverse()
        new_row, merges = merge_tiles(new_row)
        mat[i] = [0] * (SIZE - len(new_row)) + new_row[::-1]
        score += merges
    return score

def swipe_up(mat):
    score = 0
    for j in range(SIZE):
        new_col = [mat[i][j] for i in range(SIZE) if mat[i][j] != 0]
        new_col, merges = merge_tiles(new_col)
        for i in range(SIZE):
            mat[i][j] = new_col[i] if i < len(new_col) else 0
        score += merges
    return score

def swipe_down(mat):
    score = 0
    for j in range(SIZE):
        new_col = [mat[i][j] for i in range(SIZE) if mat[i][j] != 0]
        new_col.reverse()
        new_col, merges = merge_tiles(new_col)
        new_col.reverse()
        for i in range(SIZE):
            mat[i][j] = new_col[i] if i < len(new_col) else 0
        score += merges
    return score

pygame.mixer.init()
merge_sound = pygame.mixer.Sound("merge.wav")
def merge_tiles(tiles):
    score = 0
    merged = []
    skip = False
    for i in range(len(tiles)):
        if skip:
            skip = False
            continue
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            merged.append(tiles[i] * 2)
            score += tiles[i] * 2
            skip = True
            merge_sound.play()  # Play the merge sound when tiles merge
        else:
            merged.append(tiles[i])
    return merged, score

def is_game_over(mat):
    for i in range(SIZE):
        for j in range(SIZE):
            if mat[i][j] == 0 or (j < SIZE - 1 and mat[i][j] == mat[i][j + 1]) or (i < SIZE - 1 and mat[i][j] == mat[i + 1][j]):
                return False
    return True

def draw_grid(win, mat, score, high_score, game_over, username):
    win.fill((245, 245, 220)) 
    for i in range(SIZE):
        for j in range(SIZE):
            tile_value = mat[i][j]
            color = TILE_COLOR.get(tile_value, (60, 58, 50))
            pygame.draw.rect(win, color, (j * TILE_SIZE + PADDING, i * TILE_SIZE + PADDING + 100, TILE_SIZE - PADDING, TILE_SIZE - PADDING), border_radius=8)
            if tile_value > 0:
                text_color = TEXT_COLOR.get(tile_value, (255, 255, 255))
                text_surface = FONT_MAIN.render(str(tile_value), True, text_color)
                text_rect = text_surface.get_rect(center=(j * TILE_SIZE + TILE_SIZE // 2 + PADDING, i * TILE_SIZE + TILE_SIZE // 2 + 100))
                win.blit(text_surface, text_rect)
    draw_text(win, f"Score: {score}", (SIZE * TILE_SIZE + 50, 150), FONT_SCORE, (51, 0, 102))
    draw_text(win, f"High Score: {high_score}", (SIZE * TILE_SIZE + 50, 200), FONT_SCORE, (51, 0, 102))
    draw_text(win, f"Welcome, {username}!", (SIZE * TILE_SIZE + 50, 100), FONT_SCORE, (51, 0, 102))
    if game_over:
        draw_text(win, "Game Over!", (SIZE * TILE_SIZE // 2 - 50, SIZE * TILE_SIZE // 2), FONT_MAIN, (204, 0, 0))
        draw_text(win, f"Well played, {username}!", (SIZE * TILE_SIZE // 2 - 70, SIZE * TILE_SIZE // 2 + 40), FONT_SCORE, (204, 0, 0))
        draw_text(win, "Press R to Restart", (SIZE * TILE_SIZE // 2 - 50, SIZE * TILE_SIZE // 2 + 80), FONT_SCORE, (204, 0, 0))
    pygame.display.flip()



def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("2048 Deep Version")
    create_table()
    win = pygame.display.set_mode((800, 600))  # or whatever size you are using

    # Show the main menu screen first
    selected_option = main_menu_screen(win)
    
    if selected_option == "start":
        # If "Start Game" is selected, proceed to login/signup screen
        username = login_signup_screen(win)
        high_score = get_high_score(username)
        game_info_screen(win)
    elif selected_option == "about":
        # If "About" is selected, display information screen, then return to main menu
        game_info_screen(win)
        main()  # Restart main to show main menu again after "About"
    else:
        # Exit if chosen
        pygame.quit()
        sys.exit()

    # Start the game after login/signup and game info screen
    score = 0
    mat = start_game()
    clock = pygame.time.Clock()
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key == pygame.K_LEFT:
                        score += swipe_left(mat)
                        add_new(mat)
                    elif event.key == pygame.K_RIGHT:
                        score += swipe_right(mat)
                        add_new(mat)
                    elif event.key == pygame.K_UP:
                        score += swipe_up(mat)
                        add_new(mat)
                    elif event.key == pygame.K_DOWN:
                        score += swipe_down(mat)
                        add_new(mat)
                    game_over = is_game_over(mat)
                    if score > high_score:
                        high_score = score
                        save_high_score(username, high_score)
                if game_over and event.key == pygame.K_r:
                    score = 0
                    mat = start_game()
                    game_over = False
        draw_grid(win, mat, score, high_score, game_over, username)
        clock.tick(ANIMATION_SPEED)

if __name__ == "__main__":
    main()