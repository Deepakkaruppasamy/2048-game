import pygame
import random
import sys
import sqlite3
import bcrypt

SIZE = 5
TILE_SIZE = 100
PADDING = 10
WINDOW_WIDTH = SIZE * TILE_SIZE + 300
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

def draw_text(win, text, pos, font, color=(0, 0, 0)):
    text_surface = font.render(text, True, color)
    win.blit(text_surface, pos)

def draw_input_box(win, text, rect, active):
    color = (0, 0, 0) if active else (150, 150, 150)
    pygame.draw.rect(win, color, rect, 2)
    draw_text(win, text, (rect.x + 5, rect.y + 5), FONT_SCORE, (0, 0, 0))
def login_signup_screen(win):
    username, password = "", ""
    mode = "LOGIN"
    running = True
    active_input = "username"
    
    try:
        background_image = pygame.image.load("logo4.png")  
        background_image = pygame.transform.scale(background_image, (win.get_width(), win.get_height()))
        print("Background image loaded successfully.")
    except pygame.error as e:
        print(f"Error loading image: {e}")
        return

    
    game_title_pos = (win.get_width() // 2 - 100, 50)
    username_label_pos = (50, 150)
    username_rect = pygame.Rect(50, 180, 200, 30)
    password_label_pos = (50, 220)
    password_rect = pygame.Rect(50, 250, 200, 30)
    submit_instruction_pos = (50, 320)
    message = ""
    
    while running:
        win.blit(background_image, (0, 0)) 
        draw_text(win, "2048 Game", game_title_pos, FONT_MAIN, (0, 0, 0))  
        
        draw_text(win, f"{mode} - Enter your details below", (50, 110), FONT_SCORE, (0, 0, 0))  
    
        draw_text(win, "Username:", username_label_pos, FONT_SCORE, (0, 0, 0))  
        draw_input_box(win, username, username_rect, active_input == "username")
        
        draw_text(win, "Password:", password_label_pos, FONT_SCORE, (0, 0, 0))  
        draw_input_box(win, "*" * len(password), password_rect, active_input == "password")
        
        
        draw_text(win, "Press Enter to Submit, Tab to Switch Mode", submit_instruction_pos, FONT_SCORE, (0, 0, 0)) 
        draw_text(win, message, (50, 370), FONT_SCORE, (0, 0, 0))  
        
        
        if mode == "SIGNUP":
            login_button_rect = pygame.Rect(50, 400, 100, 30)
            pygame.draw.rect(win, (0, 102, 204), login_button_rect)
            draw_text(win, "Login", (login_button_rect.x + 5, login_button_rect.y + 5), FONT_SCORE, (255, 255, 255))  # Button text stays white
        
        pygame.display.flip()
        

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    active_input = "username"
                elif password_rect.collidepoint(event.pos):
                    active_input = "password"
                elif mode == "SIGNUP" and login_button_rect.collidepoint(event.pos):
                    mode = "LOGIN"
                    message = "Switched to LOGIN mode."
                    username, password = "", ""
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if active_input == "username":
                        username = username[:-1]
                    elif active_input == "password":
                        password = password[:-1]
                elif event.key == pygame.K_TAB:
                    mode = "SIGNUP" if mode == "LOGIN" else "LOGIN"
                    message = f"Switched to {mode} mode"
                elif event.key == pygame.K_RETURN:
                    if mode == "LOGIN":
                        success, message = login(username, password)
                    else:
                        success, message = signup(username, password)
                    if success:
                        return username
                elif event.unicode.isprintable():
                    if active_input == "username" and len(username) < 15:
                        username += event.unicode
                    elif active_input == "password" and len(password) < 15:
                        password += event.unicode


def game_info_screen(win):
    try:
        background_image = pygame.image.load("logo5.png")  
        background_image = pygame.transform.scale(background_image, (win.get_width(), win.get_height()))
        print("Background image loaded successfully.")
    except pygame.error as e:
        print(f"Error loading image: {e}")
        return

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
    username = login_signup_screen(win)
    high_score = get_high_score(username)
    game_info_screen(win)
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
