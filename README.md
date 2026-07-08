# snake

A terminal-based Snake game written in Python for Windows.  
It includes keyboard controls, score tracking, color themes, pause support, and several built-in cheat codes.

## Features

- Classic Snake gameplay in the terminal
- Score and high score tracking
- Pause/resume support
- Manual controls using WASD or arrow keys
- Snake color selection
- Cheat codes for speed, autopilot, instant win, and saving the high score

## Controls

### Movement
- `W`, `A`, `S`, `D` to move
- Arrow keys also supported

### Game Controls
- `P` to pause
- `Q` to quit
- `R` to restart after game over or win

## Cheat Codes

Type these during pause:

1. `nos2` - Fast
2. `sloth` - Slow
3. `mace` - Victory
4. `color` - Change Color
5. `savee` - Save high score
6. `bigdawg` - Autonomus

## How to Run

1. Make sure you have Python installed on Windows.
2. Save the game files in the same folder.
3. Run:

```bash
python snake.py
```

## Requirements

- Python 3
- Windows, because the game uses `msvcrt`

## Notes

- High score is saved in `snake_high_score.txt`
- The game uses ANSI color codes for display
- `bigdawg` enables autopilot mode
- `mace` triggers an instant win

## Disclaimer

This project is a fun terminal game. Some features may behave differently depending on your terminal support for ANSI colors.
