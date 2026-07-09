import os
import random
import time
import msvcrt
from collections import deque

WIDTH = 40
HEIGHT = 18
DELAY = 0.12
HIGH_SCORE_FILE = "snake_high_score.txt"

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# ANSI Color codes
DARK_GREEN = "\033[32m"
LIGHT_GREEN = "\033[92m"
RED = "\033[91m"
DARK_GREY = "\033[90m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
RESET = "\033[0m"

SNAKE_COLOR_THEMES = {
    "green": {"head": DARK_GREEN, "body": LIGHT_GREEN},
    "cyan": {"head": CYAN, "body": BLUE},
    "yellow": {"head": YELLOW, "body": LIGHT_GREEN},
    "magenta": {"head": "\033[95m", "body": "\033[35m"},
}


def save_high_score(high_score):
    with open(HIGH_SCORE_FILE, "w", encoding="utf-8") as file:
        file.write(str(high_score))


def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, "r", encoding="utf-8") as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0


def clear_screen():
    """Clear the console screen in a cross-platform way."""
    try:
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
    except Exception:
        pass


def spawn_food(snake):
    while True:
        food = (random.randint(1, WIDTH - 2), random.randint(1, HEIGHT - 2))
        if food not in snake:
            return food


def board_cells():
    return (WIDTH - 2) * (HEIGHT - 2)


def max_score():
    return board_cells() - 3


def full_board_snake():
    cells = []
    for y in range(1, HEIGHT - 1):
        if y % 2 == 1:
            x_values = range(1, WIDTH - 1)
        else:
            x_values = range(WIDTH - 2, 0, -1)

        for x in x_values:
            cells.append((x, y))

    return cells


def neighbors(position):
    x, y = position
    for delta in (UP, DOWN, LEFT, RIGHT):
        yield x + delta[0], y + delta[1], delta


def shortest_path_direction(snake, food):
    head = snake[0]
    blocked = set(snake[:-1])
    queue = deque([head])
    visited = {head}
    parent = {head: None}
    move_taken = {head: None}

    while queue:
        current = queue.popleft()
        if current == food:
            node = food
            while parent[node] != head and parent[node] is not None:
                node = parent[node]
            return move_taken[node]

        for next_x, next_y, delta in neighbors(current):
            next_pos = (next_x, next_y)
            if next_pos in visited:
                continue
            if next_x <= 0 or next_x >= WIDTH - 1 or next_y <= 0 or next_y >= HEIGHT - 1:
                continue
            if next_pos in blocked and next_pos != food:
                continue

            visited.add(next_pos)
            parent[next_pos] = current
            move_taken[next_pos] = delta
            queue.append(next_pos)

    return None


def path_to_tail_direction(snake):
    return shortest_path_direction(snake, snake[-1])


def safe_fallback_direction(snake, direction, food):
    head_x, head_y = snake[0]
    blocked = set(snake[:-1])
    candidates = []

    for candidate in [direction, UP, RIGHT, DOWN, LEFT]:
        if candidate not in candidates:
            candidates.append(candidate)

    best_candidate = None
    best_distance = None

    for candidate in candidates:
        next_pos = (head_x + candidate[0], head_y + candidate[1])
        if (
            0 < next_pos[0] < WIDTH - 1
            and 0 < next_pos[1] < HEIGHT - 1
            and next_pos not in blocked
        ):
            distance = abs(next_pos[0] - food[0]) + abs(next_pos[1] - food[1])
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_candidate = candidate

    return best_candidate


def is_safe_move(snake, direction):
    if not snake or direction is None:
        return False

    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    if (
        new_head[0] <= 0
        or new_head[0] >= WIDTH - 1
        or new_head[1] <= 0
        or new_head[1] >= HEIGHT - 1
    ):
        return False

    return new_head not in snake[:-1]


def draw(snake, food, score, high_score, colors):
    clear_screen()

    for y in range(HEIGHT):
        line = []
        for x in range(WIDTH):
            pos = (x, y)
            if x == 0 or x == WIDTH - 1 or y == 0 or y == HEIGHT - 1:
                # Dark grey border
                line.append(DARK_GREY + "#" + RESET)
            elif pos == snake[0]:
                line.append(colors["head"] + "O" + RESET)
            elif pos in snake[1:]:
                line.append(colors["body"] + "o" + RESET)
            elif pos == food:
                # Food - red
                line.append(RED + "*" + RESET)
            else:
                line.append(" ")
        print("".join(line))

    print(f"Score: {score}   High Score: {high_score}")
    print("Controls: W/A/S/D or arrow keys. Press P to pause, Q to quit.")


def get_direction(direction, allow_manual_input=True):
    if not msvcrt.kbhit():
        return direction, False, False

    key = msvcrt.getch()

    if key in (b"q", b"Q"):
        return direction, True, False

    if key in (b"p", b"P"):
        return direction, False, True

    if not allow_manual_input:
        return direction, False, False

    if key in (b"w", b"W"):
        new_dir = UP
    elif key in (b"s", b"S"):
        new_dir = DOWN
    elif key in (b"a", b"A"):
        new_dir = LEFT
    elif key in (b"d", b"D"):
        new_dir = RIGHT
    elif key == b"\xe0" and msvcrt.kbhit():
        key2 = msvcrt.getch()
        if key2 == b"H":
            new_dir = UP
        elif key2 == b"P":
            new_dir = DOWN
        elif key2 == b"K":
            new_dir = LEFT
        elif key2 == b"M":
            new_dir = RIGHT
        else:
            new_dir = direction
    else:
        new_dir = direction

    if (new_dir[0] != -direction[0]) or (new_dir[1] != -direction[1]):
        return new_dir, False, False

    return direction, False, False


def game_over(score, high_score):
    print(f"\nGame Over. Final score: {score}")
    print(f"High Score: {high_score}")
    print("Press R to restart or Q to quit.")

    while True:
        key = msvcrt.getch()
        if key in (b"r", b"R"):
            return True
        if key in (b"q", b"Q"):
            return False


def win_screen(score, high_score):
    print(f"\nYOU WIN. Final score: {score}")
    print(f"High Score: {high_score}")
    print("Press R to play again or Q to quit.")

    while True:
        key = msvcrt.getch()
        if key in (b"r", b"R"):
            return True
        if key in (b"q", b"Q"):
            return False


def choose_color(current_color_name):
    clear_screen()
    print("Choose Snake Color")
    print("1. Green")
    print("2. Cyan")
    print("3. Yellow")
    print("4. Magenta")
    print("Press Q to cancel.")

    while True:
        key = msvcrt.getch().lower()
        if key == b"1":
            return "green"
        if key == b"2":
            return "cyan"
        if key == b"3":
            return "yellow"
        if key == b"4":
            return "magenta"
        if key == b"q":
            return current_color_name


def game_menu(high_score, current_color_name):
    while True:
        clear_screen()
        print("=== SNAKE MENU ===")
        print("1. Start Game")
        print("2. Quit")

        key = msvcrt.getch().lower()
        if key == b"1":
            return "start", current_color_name
        if key == b"2":
            return "quit", current_color_name
        if key == b"q":
            return "quit", current_color_name


def apply_pause_cheats(typed, cheat_state, high_score):
    messages = []
    win_now = False

    if "bigdawg" in typed:
        cheat_state["aimbot_enabled"] = True
        messages.append("Cheat enabled: auto play is active.")

    if "nos2" in typed:
        cheat_state["speed_multiplier"] = 0.35
        cheat_state["speed_label"] = "NOS2"
        messages.append("Cheat enabled: speed boost activated.")

    if "sloth" in typed:
        cheat_state["speed_multiplier"] = 2.4
        cheat_state["speed_label"] = "SLOTH"
        messages.append("Cheat enabled: slow speed activated.")

    if "mace" in typed:
        cheat_state["force_win"] = True
        win_now = True
        messages.append("Cheat enabled: instant win activated.")

    if "color" in typed:
        cheat_state["open_color_picker"] = True
        messages.append("Cheat enabled: color selector opened.")

    if "savee" in typed:
        save_high_score(high_score)
        messages.append("High score saved.")

    return messages, win_now


def play_game(high_score, color_name):
    snake = [(WIDTH // 2, HEIGHT // 2)]
    snake.append((snake[0][0] - 1, snake[0][1]))
    snake.append((snake[0][0] - 2, snake[0][1]))

    direction = RIGHT
    food = spawn_food(snake)
    score = 0
    cheat_state = {
        "aimbot_enabled": False,
        "speed_multiplier": 1.0,
        "speed_label": "Normal",
        "force_win": False,
        "open_color_picker": False,
    }
    status_message = ""
    colors = SNAKE_COLOR_THEMES[color_name]

    while True:
        start = time.time()

        direction, quit_now, pause_now = get_direction(direction, not cheat_state["aimbot_enabled"])
        if quit_now:
            return None, high_score, color_name

        if pause_now:
            cheat_active_before_pause = cheat_state["aimbot_enabled"]
            draw(
                snake,
                food,
                score,
                high_score,
                colors,
            )
            if status_message:
                print(status_message)
                status_message = ""
            print("PAUSED. Press P to resume or Q to quit.")
            print(":)")
            print("")
            typed = ""
            while True:
                key = msvcrt.getch()
                if key in (b"q", b"Q"):
                    return None, high_score, color_name
                if key in (b"p", b"P"):
                    break

                if key in (b"\x00", b"\xe0"):
                    # Ignore extended key prefixes while reading cheat input.
                    continue

                try:
                    char = key.decode("utf-8").lower()
                except UnicodeDecodeError:
                    continue

                typed += char
                if len(typed) > 64:
                    typed = typed[-64:]

            if cheat_active_before_pause:
                cheat_state["aimbot_enabled"] = False
                print("Cheat disabled. Manual control restored.")

            messages, win_now = apply_pause_cheats(typed, cheat_state, high_score)
            for message in messages:
                print(message)

            if cheat_state["open_color_picker"]:
                color_name = choose_color(color_name)
                colors = SNAKE_COLOR_THEMES[color_name]
                cheat_state["open_color_picker"] = False

            if cheat_state["force_win"] or win_now:
                snake = full_board_snake()
                score = max_score()
                high_score = max(high_score, score)
                save_high_score(high_score)
                draw(
                    snake,
                    food,
                    score,
                    high_score,
                    colors,
                )
                print("YOU WIN")
                return ("win", score), high_score, color_name

        head_x, head_y = snake[0]
        if cheat_state["aimbot_enabled"]:
            try:
                path_direction = shortest_path_direction(snake, food)
                if path_direction is not None and not is_safe_move(snake, path_direction):
                    path_direction = None

                if path_direction is None:
                    path_direction = path_to_tail_direction(snake)
                    if path_direction is not None and not is_safe_move(snake, path_direction):
                        path_direction = None

                if path_direction is None:
                    path_direction = safe_fallback_direction(snake, direction, food)
            except Exception:
                path_direction = None

            if path_direction is None:
                cheat_state["aimbot_enabled"] = False
                status_message = "Auto play stopped: no safe route found."
                new_head = (head_x + direction[0], head_y + direction[1])
            else:
                direction = path_direction
                new_head = (head_x + direction[0], head_y + direction[1])
        else:
            new_head = (head_x + direction[0], head_y + direction[1])

        will_grow = new_head == food
        body_to_check = snake if will_grow else snake[:-1]

        if (
            new_head[0] <= 0
            or new_head[0] >= WIDTH - 1
            or new_head[1] <= 0
            or new_head[1] >= HEIGHT - 1
            or new_head in body_to_check
        ):
            draw(
                snake,
                food,
                score,
                high_score,
                colors,
            )
            return score, high_score, color_name

        snake.insert(0, new_head)

        if will_grow:
            score += 1
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            if len(snake) == board_cells():
                draw(
                    snake,
                    food,
                    score,
                    high_score,
                    colors,
                )
                print("YOU WIN")
                return ("win", score), high_score, color_name

            food = spawn_food(snake)
        else:
            snake.pop()

        draw(
            snake,
            food,
            score,
            high_score,
            colors,
        )
        if status_message:
            print(status_message)
            status_message = ""

        elapsed = time.time() - start
        # Compensate for character aspect ratio (~2:1 height:width)
        # Slow down vertical movement to match horizontal speed
        base_delay = DELAY * 2 if direction[0] == 0 else DELAY
        actual_delay = base_delay * cheat_state["speed_multiplier"]
        if elapsed < actual_delay:
            time.sleep(actual_delay - elapsed)


def main():
    high_score = load_high_score()
    color_name = "green"

    while True:
        action, color_name = game_menu(high_score, color_name)
        if action == "quit":
            break

        result, high_score, color_name = play_game(high_score, color_name)

        if result is None:
            continue

        if isinstance(result, tuple):
            result_type, score = result
        else:
            result_type, score = "score", result

        if score > high_score:
            high_score = score
            save_high_score(high_score)

        if result_type == "win":
            restart = win_screen(score, high_score)
            if not restart:
                break
            continue

        restart = game_over(score, high_score)
        if not restart:
            break


if __name__ == "__main__":
    main()
