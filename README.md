# Dungeon Explorer 🗡️

Welcome to **Dungeon Explorer**, a fast-paced 2D dungeon crawler built entirely in Python using OpenCV for rendering!

Navigate through **17 uniquely hand-crafted and scaling levels** of increasing difficulty. Dodge fireballs, outsmart skeletons, collect coins, and upgrade your gear at the Piggy Shop!

## 🌟 Features
- **Dynamic Camera System**: Massive dungeon floors (up to 20x20 grids) feature a smooth-scrolling camera that follows the player while keeping the UI perfectly pinned.
- **Progressive Difficulty**: Start in small tutorial rooms and end in sprawling open-arena gauntlets swarming with enemies.
- **The Piggy Shop**: Spend your hard-earned gold coins to permanently upgrade your maximum health and weapon damage.
- **Native Audio**: Background music runs seamlessly using macOS's native `afplay`—no `pygame` installation required!
- **Procedural Elements**: Monsters and fireballs patrol the dungeon randomly, making every run slightly different.

## 🚀 How to Run

### Requirements
- macOS
- Python 3
- `numpy`
- `opencv-python` (cv2)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/DhruvaBamb/dungeon-explorer.git
   cd dungeon-explorer
   ```
2. Install the required Python packages:
   ```bash
   pip3 install numpy opencv-python
   ```
3. Run the game:
   ```bash
   python3 main.py
   ```

## 🎮 Controls
- **W / A / S / D**: Move Up, Left, Down, Right
- **Q**: Quit the game
- **ESC**: Exit the Shop
- **A / D** (in shop): Cycle between items
- **SPACE** (in shop): Purchase the selected item

## ⚖️ License
Copyright (c) 2026 DhruvaBamb. All Rights Reserved.
