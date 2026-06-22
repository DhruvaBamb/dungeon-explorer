"""
graphics engine for 2D games
"""

import os
import subprocess
import numpy as np
import cv2
from game import start_game, move_player, update

TILE_PATH = os.path.split(__file__)[0] + "/tiles"

# title of the game window
GAME_TITLE = "Dungeon Explorer"

# map keyboard keys to move commands
MOVES = {
    "a": "left",
    "d": "right",
    "w": "up",
    "s": "down",
}

#
# constants measured in pixels
#
SCREEN_SIZE_X, SCREEN_SIZE_Y = 840, 640
TILE_SIZE = 64


def read_image(filename: str) -> np.ndarray:
    """
    Reads an image and resizes it to TILE_SIZE x TILE_SIZE.
    """
    img = cv2.imread(filename)

    if img is None:
        raise IOError(f"Image not found: '{filename}'")

    # Force every image to be exactly TILE_SIZE × TILE_SIZE
    img = cv2.resize(img, (TILE_SIZE, TILE_SIZE))

    return img


def read_images():
    images = {
        filename[:-4]: read_image(os.path.join(TILE_PATH, filename))
        for filename in os.listdir(TILE_PATH)
        if filename.endswith(".png")
    }
    images["wand_brass"] = read_image(os.path.join(TILE_PATH, "item", "wand_brass.png"))
    return images


def play_music():
    for filename in os.listdir(TILE_PATH):
        if filename.endswith(".mp3"):
            music_path = os.path.join(TILE_PATH, filename)
            # afplay is a built-in Mac audio player
            return subprocess.Popen(["afplay", music_path])
    return None


def draw_tile(frame, x, y, image, xbase=0, ybase=0):
    # calculate screen position in pixels
    xpos = xbase + x * TILE_SIZE
    ypos = ybase + y * TILE_SIZE

    # Safety check: resize image if needed
    if image.shape[:2] != (TILE_SIZE, TILE_SIZE):
        image = cv2.resize(image, (TILE_SIZE, TILE_SIZE))

    # Make sure we don't draw outside the screen
    if (
        xpos < 0
        or ypos < 0
        or xpos + TILE_SIZE > frame.shape[1]
        or ypos + TILE_SIZE > frame.shape[0]
    ):
        return

    # copy the image to the screen
    frame[ypos : ypos + TILE_SIZE, xpos : xpos + TILE_SIZE] = image


def draw_move(frame, move, images, camera_x=0, camera_y=0):
    draw_tile(
        frame,
        x=move.from_x - camera_x,
        y=move.from_y - camera_y,
        image=images[move.tile],
        xbase=move.progress * move.speed_x,
        ybase=move.progress * move.speed_y,
    )
    move.progress += 1


def clean_moves(game, moves):
    result = []
    for m in moves:
        if m.progress * max(abs(m.speed_x), abs(m.speed_y)) < TILE_SIZE:
            result.append(m)
        else:
            m.complete = True
            if m.finished is not None:
                m.finished(game)
    return result


def is_player_moving(moves):
    return any([m for m in moves if m.tile == "player"])


def draw(game, images, moves):
    # initialize screen
    frame = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)

    # Calculate Camera
    view_w = (SCREEN_SIZE_X + TILE_SIZE - 1) // TILE_SIZE
    view_h = (SCREEN_SIZE_Y + TILE_SIZE - 1) // TILE_SIZE
    map_h = len(game.current_level.level)
    map_w = len(game.current_level.level[0])
    
    camera_x = game.x - view_w // 2
    camera_y = game.y - view_h // 2
    
    camera_x = max(0, min(camera_x, max(0, map_w - view_w)))
    camera_y = max(0, min(camera_y, max(0, map_h - view_h)))

    # draw dungeon tiles
    for y, row in enumerate(game.current_level.level):
        for x, tile in enumerate(row):
            screen_x = x - camera_x
            screen_y = y - camera_y
            
            if 0 <= screen_x < view_w and 0 <= screen_y < view_h:
                if tile == ".":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["floor"])
                elif tile == "#":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["wall"])
                elif tile == "x":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["stairs_down"])
                elif tile == "$":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["coin"])
                elif tile == "k":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["key"])
                elif tile == "d":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["closed_door"])
                elif tile == "D":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["open_door"])
                elif tile == "t":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["teleporter"])
                elif tile == "p":
                    draw_tile(frame, x=screen_x, y=screen_y, image=images["shop"])

    # draw player
    while game.moves:
        moves.append(game.moves.pop())

    if not is_player_moving(moves):
        screen_x = game.x - camera_x
        screen_y = game.y - camera_y
        draw_tile(frame=frame, x=screen_x, y=screen_y, image=images["player"])

    # draw coin count
    cv2.putText(
        frame,
        str(game.coins),
        org=(730, 78),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.5,
        color=(255, 128, 128),
        thickness=3,
    )

    # inventory
    for i, item in enumerate(game.items):
        y = i // 2  # floor division: rounded down
        x = i % 2  # modulo: remainder of an integer division
        draw_tile(frame, xbase=660, ybase=96, x=x, y=y, image=images[item])

    # draw everything that moves
    for m in moves:
        draw_move(frame=frame, move=m, images=images, camera_x=camera_x, camera_y=camera_y)

    frame[150 : 150 + game.health, 700:740] = (0, 159, 255)
    # display complete image
    cv2.imshow(GAME_TITLE, frame)


def draw_shop(game, images):
    frame = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)

    # Draw shopkeeper
    draw_tile(frame, x=10, y=7, image=images["piggy"])

    # Draw items and boxes
    items = ["shield", "long_sword", "potion", "wand_brass", "closed_door"]
    prices = [5, 10, 20, 50, 0]
    descriptions = [
        ("Shield", "+50 max health"),
        ("Magic Sword", "+2 damage"),
        ("Potion", "Restore health"),
        ("Magic Wand", "Mystery item"),
        ("Exit", "Leave shop"),
    ]

    for i in range(5):
        x_pos = 1 + i * 2
        y_pos = 3

        # draw box
        color = (0, 255, 255) if game.shop_selection == i else (255, 255, 255)
        cv2.rectangle(
            frame,
            (x_pos * TILE_SIZE, y_pos * TILE_SIZE),
            ((x_pos + 1) * TILE_SIZE, (y_pos + 1) * TILE_SIZE),
            color,
            2,
        )

        if i < 4:
            draw_tile(frame, x=x_pos, y=y_pos, image=images[items[i]])
            cv2.putText(
                frame,
                str(prices[i]),
                (x_pos * TILE_SIZE + 10, (y_pos + 1) * TILE_SIZE + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255),
                2,
            )
        else:
            cv2.putText(
                frame,
                "EXIT",
                (x_pos * TILE_SIZE + 5, y_pos * TILE_SIZE + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

    # Draw descriptions
    desc_title, desc_sub = descriptions[game.shop_selection]
    cv2.putText(
        frame, desc_title, (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3
    )
    cv2.putText(
        frame, desc_sub, (100, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    cv2.putText(
        frame,
        "press space to select",
        (100, 500),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (128, 128, 128),
        2,
    )

    # Draw coins
    draw_tile(frame, x=10, y=1, image=images["coin"])
    cv2.putText(
        frame,
        str(game.coins),
        (11 * TILE_SIZE, 1 * TILE_SIZE + 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.5,
        (0, 255, 255),
        3,
    )

    # Draw inventory
    for i, item in enumerate(game.items):
        draw_tile(frame, x=10 + (i % 2), y=3 + (i // 2), image=images[item])

    cv2.imshow(GAME_TITLE, frame)


def handle_keyboard(game):
    """keys are mapped to move commands"""
    key = chr(cv2.waitKey(1) & 0xFF)

    if key == "q":
        game.status = "exited"
    elif key == "h":
        from game import use_potion
        use_potion(game)
    elif key == "f":
        from game import use_wand
        use_wand(game)

    return MOVES.get(key)


def main():
    images = read_images()
    music_proc = play_music()
    game = start_game()
    queued_move = None
    moves = []

    while game.status in ["running", "shop"]:
        if game.status == "running":
            draw(game, images, moves)
            moves = clean_moves(game, moves)
            update(game)

            queued_move = handle_keyboard(game)

            if not is_player_moving(moves) and queued_move:
                move_player(game, queued_move)
        elif game.status == "shop":
            draw_shop(game, images)
            key = cv2.waitKey(1) & 0xFF
            char = chr(key) if key < 256 else ""
            if char == "a":
                game.shop_selection = max(0, game.shop_selection - 1)
            elif char == "d":
                game.shop_selection = min(4, game.shop_selection + 1)
            elif char == " ":
                from game import buy_item

                buy_item(game)
            elif key == 27:  # ESC
                game.status = "running"
            elif char == "q":
                game.status = "exited"

    cv2.destroyAllWindows()
    if music_proc:
        music_proc.terminate()


if __name__ == "__main__":
    main()
