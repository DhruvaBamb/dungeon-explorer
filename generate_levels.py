import random
import re

def generate_map(w, h, shop=True, keys=2):
    grid = [["." for _ in range(w)] for _ in range(h)]
    
    # Borders
    for x in range(w):
        grid[0][x] = "#"
        grid[h-1][x] = "#"
    for y in range(h):
        grid[y][0] = "#"
        grid[y][w-1] = "#"
        
    # Bottom corridor for exit
    for x in range(1, w-1):
        grid[h-3][x] = "#"
        
    # Entrance to corridor at bottom-left
    grid[h-3][1] = "."
    
    # Exit and doors
    grid[h-2][w-2] = "x"
    for i in range(1, keys+1):
        grid[h-2][w-2 - i] = "d"
        
    # Shop in top-left
    if shop:
        grid[1][1] = "p"
        
    # Add random walls in arena (y from 1 to h-4)
    random.seed(w*h*keys)
    for _ in range((w*(h-4)) // 8):
        rx, ry = random.randint(2, w-2), random.randint(1, h-4)
        if grid[ry][rx] == ".":
            grid[ry][rx] = "#"
            
    # Place keys
    for _ in range(keys):
        placed = False
        while not placed:
            rx, ry = random.randint(2, w-2), random.randint(1, h-4)
            if grid[ry][rx] == ".":
                grid[ry][rx] = "k"
                placed = True
                
    # Place coins
    for _ in range((w*(h-4)) // 6):
        rx, ry = random.randint(2, w-2), random.randint(1, h-4)
        if grid[ry][rx] == ".":
            grid[ry][rx] = "$"
            
    # Ensure start is open
    grid[1][2] = "."
    grid[2][1] = "."
    grid[2][2] = "."
    
    lines = ["".join(row) for row in grid]
    return lines

def generate_level_code(level_num, w, h, num_fireballs, num_skeletons, keys):
    lines = generate_map(w, h, keys=keys)
    map_str = ",\n        ".join(f'"{line}"' for line in lines)
    
    fireballs = []
    random.seed(w*h*keys*2)
    for _ in range(num_fireballs):
        fx, fy = random.randint(2, w-2), random.randint(1, h-4)
        direction = random.choice(["up", "down", "left", "right"])
        fireballs.append(f'Fireball(x={fx}, y={fy}, direction="{direction}")')
    fb_str = ",\n        ".join(fireballs)
    
    skeletons = []
    for _ in range(num_skeletons):
        sx, sy = random.randint(2, w-2), random.randint(1, h-4)
        direction = random.choice(["up", "down", "left", "right"])
        skeletons.append(f'Skeleton(x={sx}, y={sy}, direction="{direction}")')
    sk_str = ",\n        ".join(skeletons)
    
    code = f"""
LEVEL_{level_num} = Level(
    level=parse_level([
        {map_str}
    ]),
    fireballs=[
        {fb_str}
    ],
    skeletons=[
        {sk_str}
    ]
)
"""
    return code

levels = [
    ("EIGHT", 12, 12, 4, 3, 2),
    ("NINE", 12, 12, 5, 4, 3),
    ("TEN", 14, 14, 6, 5, 4),
    ("ELEVEN", 14, 14, 7, 6, 5),
    ("TWELVE", 16, 16, 8, 7, 6),
    ("THIRTEEN", 16, 16, 9, 8, 7),
    ("FOURTEEN", 18, 18, 10, 9, 8),
    ("FIFTEEN", 18, 18, 11, 10, 9),
    ("SIXTEEN", 20, 20, 13, 12, 10),
    ("SEVENTEEN", 20, 20, 15, 15, 12),
    ("EIGHTEEN", 22, 22, 17, 18, 14),
    ("NINETEEN", 22, 22, 19, 21, 16),
    ("TWENTY", 24, 24, 21, 24, 18),
]

with open("/Users/dhruvasbamb/Desktop/Games_TU/game.py", "r") as f:
    content = f.read()

content = re.sub(r'LEVELS\s*=\s*\[.*?\]', '', content, flags=re.DOTALL)

if 'LEVEL_EIGHT =' in content:
    content = content.split('LEVEL_EIGHT =')[0]

for args in levels:
    content += generate_level_code(*args)
    
level_names = ["LEVEL_ONE", "LEVEL_TWO", "LEVEL_THREE", "LEVEL_FOUR", "LEVEL_FIVE", "LEVEL_SIX", "LEVEL_SEVEN"]
level_names += ["LEVEL_" + args[0] for args in levels]

content += f"\nLEVELS = [{', '.join(level_names)}]\n"

with open("/Users/dhruvasbamb/Desktop/Games_TU/game.py", "w") as f:
    f.write(content)

print("SUCCESS")
