"""
the Dungeon Explorer game logic
"""

import random
from pydantic import BaseModel
from moves import Move


class Skeleton(BaseModel):
    x: int
    y: int
    health: int = 3
    direction: str = "right"
    move: Move = None


# skeleton logic
def move_skeleton(game, skeleton):  # called by update!
    skeleton.direction = random.choice(["up", "down", "left", "right"])
    new_x, new_y = get_next_position(skeleton.x, skeleton.y, skeleton.direction)
    if game.current_level.level[new_y][new_x] in ".$k":
        skeleton.move = Move(
            tile="skeleton",
            from_x=skeleton.x,
            from_y=skeleton.y,
            speed_x=(new_x - skeleton.x) * 1,
            speed_y=(new_y - skeleton.y) * 1,
        )
        game.moves.append(skeleton.move)
        skeleton.x = new_x
        skeleton.y = new_y

        # fireball movement logic


def check_collision(game):
    for f in game.current_level.fireballs:
        if f.x == game.x and f.y == game.y:
            take_damage(game)

    for f in game.current_level.player_fireballs[:]:
        for s in game.current_level.skeletons[:]:
            if f.x == s.x and f.y == s.y:
                s.health -= game.damage + 2
                if f in game.current_level.player_fireballs:
                    game.current_level.player_fireballs.remove(f)
                if s.health <= 0 and s in game.current_level.skeletons:
                    game.current_level.skeletons.remove(s)

    for s in game.current_level.skeletons[:]:
        if s.x == game.x and s.y == game.y:
            if "long_sword" in game.items:
                game.current_level.skeletons.remove(s)
                game.sword_durability -= 1
                if game.sword_durability <= 0:
                    game.items.remove("long_sword")
            else:
                take_damage(game)


def update(game):
    for f in game.current_level.fireballs:
        if not f.move or f.move.complete:
            move_fireball(game, f)

    for f in game.current_level.player_fireballs:
        if not f.move or f.move.complete:
            move_fireball(game, f)

    # skeleton logic
    for s in game.current_level.skeletons:
        if not s.move or s.move.complete:
            move_skeleton(game, s)
    check_collision(game)


class Teleporter(BaseModel):
    x: int
    y: int
    target_x: int
    target_y: int

    # fireball


class Fireball(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None


def get_next_position(x, y, direction):
    if direction == "right":
        return x + 1, y

    elif direction == "left":
        return x - 1, y

    elif direction == "up":
        return x, y - 1

    elif direction == "down":
        return x, y + 1


def move_fireball(game, fireball):

    new_x, new_y = get_next_position(fireball.x, fireball.y, fireball.direction)

    if game.current_level.level[new_y][new_x] in ".$k":
        fireball.move = Move(
            tile="fireball",
            from_x=fireball.x,
            from_y=fireball.y,
            speed_x=(new_x - fireball.x) * 2,
            speed_y=(new_y - fireball.y) * 2,
        )
        game.moves.append(fireball.move)
        fireball.x = new_x
        fireball.y = new_y

    else:

        if fireball.direction == "right":
            fireball.direction = "left"

        elif fireball.direction == "left":
            fireball.direction = "right"

        elif fireball.direction == "up":
            fireball.direction = "down"

        elif fireball.direction == "down":
            fireball.direction = "up"


class Level(BaseModel):
    level: list[list[str]]
    teleporters: list[Teleporter] = []
    fireballs: list[Fireball] = []
    player_fireballs: list[Fireball] = []
    skeletons: list[Skeleton] = []


class DungeonGame(BaseModel):
    status: str = "running"
    x: int
    y: int
    direction: str = "right"
    moves: list[Move] = []

    coins: int = 0
    health: int = 100
    max_health: int = 100
    shield_hp: int = 0
    sword_durability: int = 0
    invisible_until: float = 0.0
    damage: int = 1
    shop_selection: int = 0

    # item
    items: list[str] = []

    current_level: Level
    level_number: int = 0


def move_player(game: DungeonGame, direction: str) -> None:
    """Things that happen when the player walks on stuff"""
    game.direction = direction
    new_x = game.x
    new_y = game.y

    if direction == "right":
        move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=2, speed_y=0)
        game.moves.append(move)
        new_x += 1

    elif direction == "left":
        move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=-2, speed_y=0)
        game.moves.append(move)
        new_x -= 1

    elif direction == "up":
        move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=0, speed_y=-2)
        game.moves.append(move)
        new_y -= 1

    elif direction == "down":
        move = Move(tile="player", from_x=game.x, from_y=game.y, speed_x=0, speed_y=2)
        game.moves.append(move)
        new_y += 1

    tile = game.current_level.level[new_y][new_x]

    # key removal logic
    if tile == "d" and "key" in game.items:
        game.items.remove("key")
        game.current_level.level[new_y][new_x] = "D"
        tile = "D"

    # collect coin
    if tile == "$":
        game.current_level.level[new_y][new_x] = "."
        game.coins += 1
        print("Coins:", game.coins)
        tile = "."

    # move on floor
    if tile == ".":
        game.x = new_x
        game.y = new_y

    # stairs
    elif tile == "x":
        game.level_number += 1
        if game.level_number < len(LEVELS):
            game.current_level = LEVELS[game.level_number]
            game.x = 1
            game.y = 1
            print("Level:", game.level_number + 1)
        else:
            game.status = "finished"

    # shop
    elif tile == "p":
        game.status = "shop"
        game.shop_selection = 0

    # keys
    if tile == "k":
        game.current_level.level[new_y][new_x] = "."
        game.items.append("key")
        print("Key:", game.items)
        tile = "."

    # Door logic
    if tile == "D":
        game.x = new_x
        game.y = new_y

    # Teleport

    if tile in "t":
        game.x = new_x
        game.y = new_y

    # Teleport
    for t in game.current_level.teleporters:
        if game.x == t.x and game.y == t.y:
            game.x = t.target_x
            game.y = t.target_y
            break

    check_collision(game)


# Fire ball movement damge logi


def parse_level(level):
    return [list(row) for row in level]


def take_damage(game):
    import time
    if time.time() < game.invisible_until:
        return

    if game.shield_hp > 0:
        game.shield_hp -= 1
        if game.shield_hp <= 0:
            if "shield" in game.items:
                game.items.remove("shield")
        return

    game.health -= 1
    if game.health <= 0:
        game.status = "game over"


def start_game():
    return DungeonGame(
        x=8,
        y=1,
        current_level=LEVEL_ONE,
        level_number=0,
    )


LEVEL_ONE = Level(
    level=parse_level(
        [
            "##########",
            "#k..$....#",
            "#..##.#..#",
            "####..####",
            "#k.....dx#",
            "#$$..t$$d#",
            "####..####",
            "#..#.##.p#",
            "#$..k.t.$#",
            "##########",
        ]
    ),
    teleporters=[
        Teleporter(x=5, y=5, target_x=6, target_y=8),
        Teleporter(x=6, y=8, target_x=5, target_y=5),
    ],
    fireballs=[
        Fireball(x=1, y=4, direction="right"),
        Fireball(x=1, y=8, direction="right"),
    ],
    skeletons=[
        Skeleton(x=4, y=1, direction="right"),
    ],
)

LEVEL_TWO = Level(
    level=parse_level(
        [
            "##########",
            "#.##$....#",
            "#..#.#p..#",
            "##.#.##.##",
            "#..#....$#",
            "#.######.#",
            "#.$....#.#",
            "####.#.#.#",
            "#x...#...#",
            "##########",
        ]
    ),
    skeletons=[
        Skeleton(x=8, y=1, direction="left"),
        Skeleton(x=1, y=6, direction="right"),
        Skeleton(x=8, y=8, direction="up"),
    ],
)

LEVEL_THREE = Level(
    level=parse_level(
        [
            "##########",
            "#........#",
            "#.######.#",
            "#.#..k.#.#",
            "#.#.##.#$#",
            "#...##...#",
            "#.####.#d#",
            "#....$...#",
            "#.###p##x#",
            "##########",
        ]
    ),
    fireballs=[
        Fireball(x=1, y=7, direction="right"),
        Fireball(x=8, y=7, direction="left"),
        Fireball(x=2, y=1, direction="right"),
        Fireball(x=7, y=1, direction="left"),
    ],
)

LEVEL_FOUR = Level(
    level=parse_level(
        [
            "##########",
            "#..##p$$$#",
            "#.t##...t#",
            "##########",
            "#k.##....#",
            "#.t##.t..#",
            "#####.####",
            "#...#.####",
            "#.t.#.dx.#",
            "##########",
        ]
    ),
    teleporters=[
        Teleporter(x=2, y=2, target_x=5, target_y=2),
        Teleporter(x=8, y=2, target_x=2, target_y=4),
        Teleporter(x=2, y=5, target_x=8, target_y=4),
        Teleporter(x=6, y=5, target_x=1, target_y=7),
        Teleporter(x=2, y=8, target_x=5, target_y=8),
    ],
    skeletons=[Skeleton(x=7, y=4, direction="down")],
)

LEVEL_FIVE = Level(
    level=parse_level(
        [
            "##########",
            "#p$$$$$$k#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#........#",
            "#k.....dx#",
            "##########",
        ]
    ),
    fireballs=[
        Fireball(x=3, y=3, direction="down"),
        Fireball(x=5, y=5, direction="right"),
        Fireball(x=7, y=2, direction="up"),
    ],
    skeletons=[
        Skeleton(x=2, y=6, direction="right"),
        Skeleton(x=6, y=6, direction="left"),
        Skeleton(x=4, y=4, direction="up"),
        Skeleton(x=8, y=8, direction="left"),
    ],
)

LEVEL_SIX = Level(
    level=parse_level([
        "##########",
        "#p#...#..#",
        "#.#.#.#..#",
        "#........#",
        "#.#.###.##",
        "#........#",
        "##.#...#.#",
        "#........#",
        "#k#...#dx#",
        "##########",
    ]),
    fireballs=[
        Fireball(x=1, y=3, direction="right"),
        Fireball(x=8, y=5, direction="left"),
        Fireball(x=1, y=7, direction="right"),
        Fireball(x=3, y=1, direction="down"),
        Fireball(x=5, y=8, direction="up"),
        Fireball(x=7, y=1, direction="down")
    ],
    skeletons=[
        Skeleton(x=2, y=8, direction="right"),
        Skeleton(x=6, y=2, direction="left")
    ]
)

LEVEL_SEVEN = Level(
    level=parse_level([
        "##########",
        "#p$.....k#",
        "#$.......#",
        "#........#",
        "#........#",
        "#........#",
        "#........#",
        "#..#######",
        "#k.ddx...#",
        "##########",
    ]),
    fireballs=[
        Fireball(x=3, y=3, direction="down"),
        Fireball(x=6, y=6, direction="up"),
        Fireball(x=2, y=6, direction="right"),
        Fireball(x=7, y=2, direction="left"),
    ],
    skeletons=[
        Skeleton(x=4, y=4, direction="right"),
        Skeleton(x=5, y=3, direction="left"),
        Skeleton(x=3, y=5, direction="up"),
        Skeleton(x=6, y=4, direction="down"),
        Skeleton(x=8, y=6, direction="left"),
    ]
)




def buy_item(game):
    prices = [5, 10, 20, 50, 0]
    if game.shop_selection == 4:
        game.status = "running"
        return

    if game.coins >= prices[game.shop_selection]:
        game.coins -= prices[game.shop_selection]
        if game.shop_selection == 0:
            game.items.append("shield")
            game.shield_hp = 50
        elif game.shop_selection == 1:
            game.items.append("long_sword")
            game.sword_durability = 2
            game.damage += 2
        elif game.shop_selection == 2:
            game.items.append("potion")
        elif game.shop_selection == 3:
            game.items.append("wand_brass")

def use_potion(game):
    if "potion" in game.items:
        game.items.remove("potion")
        game.health = min(game.max_health, game.health + 50)

def use_wand(game):
    import time
    if "wand_brass" in game.items:
        game.items.remove("wand_brass")
        game.invisible_until = time.time() + 30.0


LEVEL_EIGHT = Level(
    level=parse_level([
        "############",
        "#p....$$.$.#",
        "#........$.#",
        "#......#.#.#",
        "#..$k.....k#",
        "#.......$.$#",
        "#..#....##.#",
        "#.#..$...#.#",
        "#.#.#.#$.#$#",
        "#.##########",
        "#.......ddx#",
        "############"
    ]),
    fireballs=[
        Fireball(x=9, y=4, direction="up"),
        Fireball(x=7, y=7, direction="up"),
        Fireball(x=5, y=5, direction="right"),
        Fireball(x=6, y=3, direction="up")
    ],
    skeletons=[
        Skeleton(x=7, y=5, direction="down"),
        Skeleton(x=7, y=7, direction="down"),
        Skeleton(x=4, y=8, direction="right")
    ]
)

LEVEL_NINE = Level(
    level=parse_level([
        "############",
        "#p...$...#.#",
        "#..k#.#k.#$#",
        "#.$...$...##",
        "#...##...#.#",
        "#..$$.$#$$.#",
        "#.........##",
        "#....k$$..$#",
        "#....#$.#..#",
        "#.##########",
        "#......dddx#",
        "############"
    ]),
    fireballs=[
        Fireball(x=6, y=8, direction="up"),
        Fireball(x=7, y=4, direction="down"),
        Fireball(x=3, y=1, direction="down"),
        Fireball(x=7, y=5, direction="left"),
        Fireball(x=8, y=3, direction="up")
    ],
    skeletons=[
        Skeleton(x=6, y=4, direction="down"),
        Skeleton(x=4, y=1, direction="down"),
        Skeleton(x=7, y=8, direction="left"),
        Skeleton(x=10, y=5, direction="left")
    ]
)

LEVEL_TEN = Level(
    level=parse_level([
        "##############",
        "#p..#$.$.....#",
        "#....##.k....#",
        "#....$.#..$.$#",
        "#....$$.$$k..#",
        "#.#..#......##",
        "#.$....$##k#.#",
        "#......$#.$..#",
        "#....k$##.$.##",
        "#.$...$.#.$..#",
        "#...#$..#....#",
        "#.############",
        "#.......ddddx#",
        "##############"
    ]),
    fireballs=[
        Fireball(x=9, y=8, direction="up"),
        Fireball(x=4, y=10, direction="right"),
        Fireball(x=8, y=7, direction="up"),
        Fireball(x=3, y=8, direction="left"),
        Fireball(x=9, y=4, direction="down"),
        Fireball(x=2, y=1, direction="up")
    ],
    skeletons=[
        Skeleton(x=11, y=6, direction="right"),
        Skeleton(x=8, y=8, direction="left"),
        Skeleton(x=2, y=1, direction="up"),
        Skeleton(x=6, y=4, direction="down"),
        Skeleton(x=4, y=6, direction="down")
    ]
)

LEVEL_ELEVEN = Level(
    level=parse_level([
        "##############",
        "#p.#.....k.$.#",
        "#.........##$#",
        "#....#.$.....#",
        "#...#..#...k.#",
        "#....$###...$#",
        "#.$.#k#......#",
        "#.$.....$.$.##",
        "#...$.k..$k..#",
        "#...#..$#....#",
        "#.$........#.#",
        "#.############",
        "#......dddddx#",
        "##############"
    ]),
    fireballs=[
        Fireball(x=6, y=7, direction="left"),
        Fireball(x=7, y=8, direction="right"),
        Fireball(x=9, y=10, direction="right"),
        Fireball(x=8, y=6, direction="down"),
        Fireball(x=11, y=4, direction="left"),
        Fireball(x=2, y=3, direction="up"),
        Fireball(x=3, y=6, direction="up")
    ],
    skeletons=[
        Skeleton(x=6, y=2, direction="down"),
        Skeleton(x=7, y=1, direction="right"),
        Skeleton(x=8, y=6, direction="up"),
        Skeleton(x=7, y=7, direction="left"),
        Skeleton(x=4, y=10, direction="down"),
        Skeleton(x=4, y=2, direction="up")
    ]
)

LEVEL_TWELVE = Level(
    level=parse_level([
        "################",
        "#p...$.$.......#",
        "#..#.....$.k$..#",
        "#........#...###",
        "#.....k.....$#.#",
        "#....$...#.k$..#",
        "#..#$##..$.#...#",
        "#.....##$......#",
        "#..$.......$####",
        "#.$..k.#.$#..#.#",
        "#....#$$..#k...#",
        "#.$.......k..#$#",
        "#..$.$$......#.#",
        "#.##############",
        "#.......ddddddx#",
        "################"
    ]),
    fireballs=[
        Fireball(x=4, y=10, direction="up"),
        Fireball(x=12, y=8, direction="right"),
        Fireball(x=4, y=8, direction="up"),
        Fireball(x=4, y=8, direction="right"),
        Fireball(x=14, y=6, direction="down"),
        Fireball(x=7, y=9, direction="up"),
        Fireball(x=8, y=4, direction="left"),
        Fireball(x=14, y=6, direction="down")
    ],
    skeletons=[
        Skeleton(x=11, y=8, direction="up"),
        Skeleton(x=13, y=2, direction="down"),
        Skeleton(x=9, y=8, direction="down"),
        Skeleton(x=7, y=5, direction="up"),
        Skeleton(x=7, y=3, direction="left"),
        Skeleton(x=7, y=8, direction="down"),
        Skeleton(x=7, y=5, direction="down")
    ]
)

LEVEL_THIRTEEN = Level(
    level=parse_level([
        "################",
        "#p.....#....#..#",
        "#..$$.......k#$#",
        "#..#.$...$.##..#",
        "#...k$$...$.$..#",
        "#....$.$$.....k#",
        "#.#...$.##...#.#",
        "#..#...$.k.....#",
        "#......$k.#..#.#",
        "#....#..$...#k##",
        "#...$.$.$...#k.#",
        "#....$#.#..#$..#",
        "#.....#......#.#",
        "#.##############",
        "#......dddddddx#",
        "################"
    ]),
    fireballs=[
        Fireball(x=13, y=8, direction="down"),
        Fireball(x=2, y=9, direction="right"),
        Fireball(x=6, y=5, direction="down"),
        Fireball(x=4, y=11, direction="up"),
        Fireball(x=14, y=3, direction="up"),
        Fireball(x=6, y=8, direction="right"),
        Fireball(x=14, y=11, direction="left"),
        Fireball(x=2, y=8, direction="up"),
        Fireball(x=4, y=3, direction="up")
    ],
    skeletons=[
        Skeleton(x=8, y=10, direction="up"),
        Skeleton(x=14, y=6, direction="up"),
        Skeleton(x=8, y=11, direction="left"),
        Skeleton(x=13, y=3, direction="left"),
        Skeleton(x=4, y=10, direction="down"),
        Skeleton(x=3, y=6, direction="down"),
        Skeleton(x=12, y=5, direction="down"),
        Skeleton(x=4, y=4, direction="left")
    ]
)

LEVEL_FOURTEEN = Level(
    level=parse_level([
        "##################",
        "#p.$.##.....#$.#.#",
        "#..$k......$k...$#",
        "#..#....$..$.....#",
        "#.$...##...$..#..#",
        "#......#..##..$$.#",
        "#.k..$....#......#",
        "#.....$........k.#",
        "#........###$.#..#",
        "#............$.k##",
        "#..$...$##.#.....#",
        "#.#$.k.......#.$.#",
        "#.......#.#.....$#",
        "#.kk#.......#...$#",
        "#...$.$$..$.$#...#",
        "#.################",
        "#.......ddddddddx#",
        "##################"
    ]),
    fireballs=[
        Fireball(x=16, y=2, direction="up"),
        Fireball(x=5, y=11, direction="right"),
        Fireball(x=3, y=14, direction="down"),
        Fireball(x=15, y=8, direction="down"),
        Fireball(x=8, y=3, direction="right"),
        Fireball(x=4, y=11, direction="down"),
        Fireball(x=15, y=10, direction="left"),
        Fireball(x=13, y=5, direction="up"),
        Fireball(x=3, y=13, direction="down"),
        Fireball(x=3, y=5, direction="down")
    ],
    skeletons=[
        Skeleton(x=14, y=10, direction="up"),
        Skeleton(x=16, y=12, direction="right"),
        Skeleton(x=5, y=8, direction="up"),
        Skeleton(x=11, y=12, direction="up"),
        Skeleton(x=6, y=13, direction="down"),
        Skeleton(x=11, y=13, direction="up"),
        Skeleton(x=5, y=5, direction="left"),
        Skeleton(x=7, y=2, direction="up"),
        Skeleton(x=10, y=1, direction="left")
    ]
)

LEVEL_FIFTEEN = Level(
    level=parse_level([
        "##################",
        "#p.#.##....#$..#$#",
        "#......$......kk.#",
        "#..#.#..$.$.#.$..#",
        "#.##.....#..$.##.#",
        "#.k$...$.......#.#",
        "#...#$.#....$$$k.#",
        "#..k...$.#.#.$...#",
        "#...k$$..$$.$.$..#",
        "#....$$..#......$#",
        "#..$.$......#.k.##",
        "#.k....$$.$.##...#",
        "#.$#........#.$..#",
        "#.#......##...$$.#",
        "#.....$k.........#",
        "#.################",
        "#......dddddddddx#",
        "##################"
    ]),
    fireballs=[
        Fireball(x=11, y=10, direction="right"),
        Fireball(x=14, y=9, direction="left"),
        Fireball(x=11, y=11, direction="right"),
        Fireball(x=13, y=12, direction="down"),
        Fireball(x=15, y=4, direction="left"),
        Fireball(x=15, y=11, direction="right"),
        Fireball(x=15, y=12, direction="down"),
        Fireball(x=4, y=13, direction="up"),
        Fireball(x=3, y=14, direction="right"),
        Fireball(x=5, y=6, direction="down"),
        Fireball(x=3, y=5, direction="up")
    ],
    skeletons=[
        Skeleton(x=16, y=9, direction="left"),
        Skeleton(x=13, y=10, direction="up"),
        Skeleton(x=9, y=3, direction="right"),
        Skeleton(x=10, y=4, direction="right"),
        Skeleton(x=10, y=12, direction="down"),
        Skeleton(x=3, y=1, direction="down"),
        Skeleton(x=9, y=1, direction="left"),
        Skeleton(x=7, y=3, direction="up"),
        Skeleton(x=9, y=5, direction="down"),
        Skeleton(x=6, y=3, direction="up")
    ]
)

LEVEL_SIXTEEN = Level(
    level=parse_level([
        "####################",
        "#p.............$...#",
        "#..#$..$...kk......#",
        "#.$....#.$#.#......#",
        "#..##.$.....##.....#",
        "#..$...$.#.k.##$#$.#",
        "#.....#.$.$..$..$$.#",
        "#...#..#...$k..#...#",
        "#.......kk$....##..#",
        "#.#k...$...$.#.....#",
        "#....$...$.##..#.#.#",
        "#..#..$..#$$.#.....#",
        "#....#.$....$.#.$.##",
        "#.#.$$..#...#k..$..#",
        "#.$$...........#.$.#",
        "#....$..$...#.....##",
        "#...$..k.k...$.....#",
        "#.##################",
        "#.......ddddddddddx#",
        "####################"
    ]),
    fireballs=[
        Fireball(x=13, y=2, direction="left"),
        Fireball(x=4, y=12, direction="right"),
        Fireball(x=5, y=8, direction="down"),
        Fireball(x=3, y=4, direction="up"),
        Fireball(x=8, y=11, direction="right"),
        Fireball(x=3, y=1, direction="down"),
        Fireball(x=12, y=12, direction="right"),
        Fireball(x=18, y=5, direction="right"),
        Fireball(x=2, y=8, direction="right"),
        Fireball(x=2, y=16, direction="up"),
        Fireball(x=7, y=11, direction="up"),
        Fireball(x=15, y=1, direction="up"),
        Fireball(x=5, y=3, direction="right")
    ],
    skeletons=[
        Skeleton(x=4, y=15, direction="left"),
        Skeleton(x=6, y=12, direction="down"),
        Skeleton(x=18, y=7, direction="right"),
        Skeleton(x=11, y=15, direction="right"),
        Skeleton(x=11, y=11, direction="left"),
        Skeleton(x=14, y=2, direction="down"),
        Skeleton(x=7, y=11, direction="down"),
        Skeleton(x=5, y=8, direction="left"),
        Skeleton(x=3, y=14, direction="left"),
        Skeleton(x=9, y=14, direction="down"),
        Skeleton(x=9, y=15, direction="down"),
        Skeleton(x=2, y=5, direction="up")
    ]
)

LEVEL_SEVENTEEN = Level(
    level=parse_level([
        "####################",
        "#p.#...k.#.#..##...#",
        "#..k...#$..#.$.....#",
        "#.........#.#..$.$##",
        "#.#...#$....$.$.k#.#",
        "#..$....$.#k#....k.#",
        "#.k$$..k#...#..##$##",
        "#.$...#.$..........#",
        "#........$$....$#.$#",
        "#.#...............k#",
        "#.$$..#........#.$##",
        "#...$...$$..###....#",
        "#..#.$..#.#..$.....#",
        "#....#..$...k#..$..#",
        "#.#$..#.....$.$#...#",
        "#...$$..$..k$...k.k#",
        "#....$...#...$..$$$#",
        "#.##################",
        "#.....ddddddddddddx#",
        "####################"
    ]),
    fireballs=[
        Fireball(x=16, y=9, direction="right"),
        Fireball(x=16, y=3, direction="up"),
        Fireball(x=15, y=10, direction="right"),
        Fireball(x=2, y=15, direction="down"),
        Fireball(x=3, y=6, direction="down"),
        Fireball(x=13, y=3, direction="right"),
        Fireball(x=14, y=11, direction="down"),
        Fireball(x=2, y=9, direction="left"),
        Fireball(x=10, y=8, direction="up"),
        Fireball(x=18, y=1, direction="right"),
        Fireball(x=17, y=13, direction="down"),
        Fireball(x=11, y=13, direction="up"),
        Fireball(x=5, y=9, direction="down"),
        Fireball(x=8, y=1, direction="right"),
        Fireball(x=13, y=10, direction="right")
    ],
    skeletons=[
        Skeleton(x=18, y=4, direction="up"),
        Skeleton(x=15, y=1, direction="left"),
        Skeleton(x=15, y=1, direction="down"),
        Skeleton(x=7, y=13, direction="down"),
        Skeleton(x=2, y=7, direction="right"),
        Skeleton(x=6, y=1, direction="up"),
        Skeleton(x=6, y=16, direction="down"),
        Skeleton(x=15, y=6, direction="right"),
        Skeleton(x=3, y=3, direction="right"),
        Skeleton(x=6, y=11, direction="right"),
        Skeleton(x=6, y=9, direction="right"),
        Skeleton(x=3, y=2, direction="left"),
        Skeleton(x=15, y=4, direction="down"),
        Skeleton(x=10, y=7, direction="right"),
        Skeleton(x=17, y=16, direction="down")
    ]
)

LEVEL_EIGHTEEN = Level(
    level=parse_level([
        "######################",
        "#p..$.k..$...##.#k#.$#",
        "#......$#.#..k.....k.#",
        "#...##..kk$$.....k#..#",
        "#...##.$#k...k......k#",
        "#.$..#...$.$......$..#",
        "#......$..#.$#.k.$.$.#",
        "#.$#.#...#.#.#.$.$...#",
        "#.....#.$....$....$..#",
        "#..#....$...$$#.#...$#",
        "#..#.$...$..#........#",
        "#.......#....$$.#..$.#",
        "#..$$$.....$......$..#",
        "#..k$...#...$$.##....#",
        "#........$...$##.....#",
        "#..#..#..$.$$...$.#..#",
        "#....#.#............$#",
        "#...#$...$.....#...#.#",
        "#.$#.....kk.$#.##....#",
        "#.####################",
        "#.....ddddddddddddddx#",
        "######################"
    ]),
    fireballs=[
        Fireball(x=18, y=8, direction="right"),
        Fireball(x=17, y=5, direction="left"),
        Fireball(x=5, y=1, direction="left"),
        Fireball(x=19, y=2, direction="right"),
        Fireball(x=20, y=9, direction="right"),
        Fireball(x=19, y=18, direction="right"),
        Fireball(x=5, y=9, direction="right"),
        Fireball(x=20, y=4, direction="up"),
        Fireball(x=9, y=13, direction="right"),
        Fireball(x=2, y=2, direction="up"),
        Fireball(x=14, y=2, direction="right"),
        Fireball(x=11, y=18, direction="down"),
        Fireball(x=16, y=13, direction="left"),
        Fireball(x=13, y=8, direction="left"),
        Fireball(x=3, y=8, direction="right"),
        Fireball(x=12, y=12, direction="down"),
        Fireball(x=13, y=2, direction="up")
    ],
    skeletons=[
        Skeleton(x=14, y=2, direction="left"),
        Skeleton(x=16, y=15, direction="left"),
        Skeleton(x=14, y=14, direction="up"),
        Skeleton(x=5, y=4, direction="right"),
        Skeleton(x=17, y=6, direction="down"),
        Skeleton(x=8, y=8, direction="right"),
        Skeleton(x=5, y=8, direction="down"),
        Skeleton(x=14, y=10, direction="right"),
        Skeleton(x=4, y=3, direction="right"),
        Skeleton(x=5, y=15, direction="right"),
        Skeleton(x=13, y=8, direction="right"),
        Skeleton(x=17, y=18, direction="left"),
        Skeleton(x=5, y=4, direction="down"),
        Skeleton(x=6, y=13, direction="left"),
        Skeleton(x=11, y=12, direction="up"),
        Skeleton(x=17, y=14, direction="up"),
        Skeleton(x=2, y=3, direction="down"),
        Skeleton(x=7, y=9, direction="right")
    ]
)

LEVEL_NINETEEN = Level(
    level=parse_level([
        "######################",
        "#p.##..$..$..$$.$#$..#",
        "#.....#$........$$.#.#",
        "#..k.kk..$..$..$..#$.#",
        "#....k....##$k.$.$...#",
        "#.$k.##$.......#..$..#",
        "#.$##....#..###.....##",
        "#.#..$.$....$.$......#",
        "#.....$..#....k#.....#",
        "#....$k....###....$$.#",
        "#........k....$$#....#",
        "#..k$.k$k.k..........#",
        "#..$#.$.....#.$.#.$..#",
        "#....#............#.$#",
        "#.$$#.##.#.$...$##...#",
        "#......k.$.$.$.k....$#",
        "#...$.#....$.#.$.#...#",
        "#.......$.#k#.....#..#",
        "#..$.#.$.#..$.$......#",
        "#.####################",
        "#...ddddddddddddddddx#",
        "######################"
    ]),
    fireballs=[
        Fireball(x=11, y=1, direction="up"),
        Fireball(x=18, y=13, direction="right"),
        Fireball(x=4, y=18, direction="left"),
        Fireball(x=10, y=15, direction="left"),
        Fireball(x=17, y=8, direction="right"),
        Fireball(x=13, y=3, direction="right"),
        Fireball(x=10, y=13, direction="up"),
        Fireball(x=10, y=4, direction="up"),
        Fireball(x=20, y=1, direction="right"),
        Fireball(x=16, y=8, direction="right"),
        Fireball(x=4, y=16, direction="right"),
        Fireball(x=3, y=17, direction="down"),
        Fireball(x=19, y=5, direction="down"),
        Fireball(x=11, y=11, direction="down"),
        Fireball(x=10, y=15, direction="up"),
        Fireball(x=12, y=8, direction="down"),
        Fireball(x=6, y=12, direction="up"),
        Fireball(x=20, y=11, direction="up"),
        Fireball(x=5, y=2, direction="left")
    ],
    skeletons=[
        Skeleton(x=13, y=5, direction="up"),
        Skeleton(x=15, y=18, direction="right"),
        Skeleton(x=2, y=13, direction="down"),
        Skeleton(x=20, y=12, direction="up"),
        Skeleton(x=16, y=11, direction="down"),
        Skeleton(x=20, y=9, direction="left"),
        Skeleton(x=13, y=14, direction="down"),
        Skeleton(x=19, y=17, direction="left"),
        Skeleton(x=12, y=2, direction="left"),
        Skeleton(x=12, y=1, direction="down"),
        Skeleton(x=6, y=3, direction="right"),
        Skeleton(x=16, y=9, direction="up"),
        Skeleton(x=16, y=6, direction="down"),
        Skeleton(x=16, y=12, direction="right"),
        Skeleton(x=13, y=9, direction="right"),
        Skeleton(x=17, y=10, direction="left"),
        Skeleton(x=12, y=2, direction="up"),
        Skeleton(x=12, y=10, direction="left"),
        Skeleton(x=3, y=18, direction="up"),
        Skeleton(x=12, y=9, direction="down"),
        Skeleton(x=12, y=16, direction="up")
    ]
)

LEVEL_TWENTY = Level(
    level=parse_level([
        "########################",
        "#p...$.$........#.....$#",
        "#..#.k..##.k$$...#...$.#",
        "#...$$.$..$.$##.$......#",
        "#.#....$........$.$...$#",
        "#..#k#.......$..$......#",
        "#.....k.$$..$.#...#$.$.#",
        "#.k.#....#.$$....#k#.k.#",
        "#.$....$...$.$..#.#....#",
        "#..#.#...#..#$.$..#$.$.#",
        "#....#k.$.##..##.#....k#",
        "#...#..$.......#....kk$#",
        "#.$.$.....#k.k.......###",
        "#..#.$.$#....#.$.#.$...#",
        "#..#$..$.......$##.....#",
        "#.#...$#$#...k.#...#.$.#",
        "#.$.#...#k...$.$...$...#",
        "#..........$..#$$#...$.#",
        "#.........##..$....#.$.#",
        "#.$.$.#.#..k#.k$$....$.#",
        "#..$.k.................#",
        "#.######################",
        "#...ddddddddddddddddddx#",
        "########################"
    ]),
    fireballs=[
        Fireball(x=2, y=19, direction="up"),
        Fireball(x=6, y=6, direction="left"),
        Fireball(x=13, y=15, direction="down"),
        Fireball(x=10, y=11, direction="down"),
        Fireball(x=9, y=13, direction="up"),
        Fireball(x=4, y=6, direction="left"),
        Fireball(x=13, y=11, direction="left"),
        Fireball(x=19, y=20, direction="up"),
        Fireball(x=22, y=3, direction="down"),
        Fireball(x=7, y=12, direction="left"),
        Fireball(x=10, y=1, direction="left"),
        Fireball(x=3, y=16, direction="right"),
        Fireball(x=2, y=12, direction="right"),
        Fireball(x=16, y=14, direction="down"),
        Fireball(x=16, y=7, direction="right"),
        Fireball(x=17, y=19, direction="right"),
        Fireball(x=11, y=11, direction="up"),
        Fireball(x=4, y=9, direction="down"),
        Fireball(x=7, y=10, direction="down"),
        Fireball(x=17, y=20, direction="right"),
        Fireball(x=9, y=12, direction="left")
    ],
    skeletons=[
        Skeleton(x=9, y=17, direction="up"),
        Skeleton(x=17, y=4, direction="down"),
        Skeleton(x=2, y=1, direction="left"),
        Skeleton(x=2, y=8, direction="up"),
        Skeleton(x=18, y=4, direction="right"),
        Skeleton(x=20, y=12, direction="left"),
        Skeleton(x=18, y=17, direction="down"),
        Skeleton(x=13, y=12, direction="left"),
        Skeleton(x=4, y=16, direction="left"),
        Skeleton(x=19, y=20, direction="left"),
        Skeleton(x=21, y=6, direction="down"),
        Skeleton(x=9, y=5, direction="right"),
        Skeleton(x=14, y=2, direction="left"),
        Skeleton(x=17, y=15, direction="up"),
        Skeleton(x=6, y=18, direction="right"),
        Skeleton(x=20, y=12, direction="right"),
        Skeleton(x=19, y=20, direction="right"),
        Skeleton(x=2, y=19, direction="down"),
        Skeleton(x=21, y=20, direction="down"),
        Skeleton(x=10, y=10, direction="left"),
        Skeleton(x=10, y=7, direction="down"),
        Skeleton(x=2, y=1, direction="up"),
        Skeleton(x=6, y=8, direction="up"),
        Skeleton(x=21, y=7, direction="left")
    ]
)

LEVELS = [LEVEL_ONE, LEVEL_TWO, LEVEL_THREE, LEVEL_FOUR, LEVEL_FIVE, LEVEL_SIX, LEVEL_SEVEN, LEVEL_EIGHT, LEVEL_NINE, LEVEL_TEN, LEVEL_ELEVEN, LEVEL_TWELVE, LEVEL_THIRTEEN, LEVEL_FOURTEEN, LEVEL_FIFTEEN, LEVEL_SIXTEEN, LEVEL_SEVENTEEN, LEVEL_EIGHTEEN, LEVEL_NINETEEN, LEVEL_TWENTY]
