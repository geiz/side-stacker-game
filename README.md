# Side Stacker Game

## Overview
This is a **Sideways Connect 4** game built using **Phaser 3**. The game allows two players to compete in real-time multiplayer or play against an AI opponent with two difficulty levels.

## Features
- **Side Stacking Mechanic**: Players drop pieces into the board from the left or right side.
- **Multiplayer Mode**: Real-time rooms powered by **Socket.io**.
- **AI Opponent**:
  - **Easy AI**: Random moves.
  - **Medium AI**: Blocks opponent and aims to win based on procedural programming
  - **Hard AI**: Blocks opponent and aims to win based on AI decisions.
- **Win Detection**: Automatically checks for four-in-a-row horizontally, vertically, or diagonally.

## Installation

### 1. Clone the Repository
```sh
 git clone git@github.com:geiz/side-stacker-game.git
 cd side-stacker-game
```

### 2. Install Dependencies
```sh
npm install
```
This installs **Phaser** and **Socket.io-client**.

### 3. Start the Game
#### Run a Development Server
```sh
npm start
```
Then, open `http://localhost:3000` in your browser.

## How to Play
- Click on a **row** to place your piece on either **left or right**.
- First player to get **four-in-a-row** wins.
- Choose between **Multiplayer** or **AI Mode**.

## File Structure
```
📂 side-stacker-game/
 ├── 📂 src/
 │   ├── 📂 scenes/
 │   │   ├── Boot.js
 │   │   ├── Game.js  (Game logic)
 │   │   ├── GameOver.js
 │   │   ├── Preloader.js
 │   ├── main.js  (Game entry point)
 ├── index.html  (Main game page)
 ├── package.json  (Dependencies)
 ├── README.md  (You are here!)
```

## Future Improvements
- Add a **hard AI mode** with Monte Carlo Tree Search (MCTS).
- Improve **UI animations** for moves and win effects.

## License
MIT License. Feel free to modify and use the game! 🚀

