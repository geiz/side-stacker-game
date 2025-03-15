import { EventBus } from '../EventBus';
import Phaser from 'phaser';

export class Game extends Phaser.Scene {
    constructor() {
        super('Game');
        this.boardSize = 7;
        this.board = this.createBoard(this.boardSize, this.boardSize);
        this.currentPlayer = 'X';
        this.isAI = false;
        this.aiDifficulty = 'easy';
    }

    // Preloads assets for the game
    preload() {
        this.load.image('background', 'assets/background.png');
    }

    // Initializes the game scene
    create() {
        this.cameras.main.setBackgroundColor(0x87CEEB);
        this.add.image(400, 300, 'background').setAlpha(0.5);

        this.add.text(400, 50, 'Side Stacker Game', {
            fontFamily: 'Arial Black', fontSize: 32, color: '#ffffff',
            stroke: '#000000', strokeThickness: 6,
            align: 'center'
        }).setOrigin(0.5);

        this.addUI();
        this.setupEvents();
        EventBus.emit('current-scene-ready', this);
    }

    // Changes to the Game Over scene
    changeScene() {
        this.scene.start('GameOver');
    }

    // Creates an empty game board
    createBoard(rows, cols) {
        return Array.from({ length: rows }, () => Array(cols).fill(null));
    }

    // Adds UI elements to the game
    addUI() {
        this.graphics = this.add.graphics();
        this.graphics.fillStyle(0xbbada0, 0.9);
        this.graphics.fillRoundedRect(100, 100, 600, 600, 16);
        this.input.on('pointerdown', this.handleClick, this);
    }

    // Sets up event listeners
    setupEvents() {
        EventBus.on('start-game', ({ mode, difficulty }) => {
            this.isAI = mode === 'AI';
            this.aiDifficulty = difficulty;
            this.resetGame();
        });
    }

    // Handles user input when clicking the board
    handleClick(pointer) {
        const row = Math.floor((pointer.y - 100) / 85);
        const side = pointer.x < 400 ? 'L' : 'R';
        this.makeMove(row, side);
    }

    // Processes a player's move
    makeMove(row, side) {
        let col = side === 'L' ? 0 : this.boardSize - 1;
        while (this.board[row][col] !== null) {
            col += side === 'L' ? 1 : -1;
            if (col < 0 || col >= this.boardSize) return;
        }
        this.board[row][col] = this.currentPlayer;
        this.drawBoard();
        if (this.checkWin()) {
            EventBus.emit('game-over', this.currentPlayer);
        } 
    }

    

    // Checks if there is a winner on the board
    checkWin(board = this.board) {
        const directions = [
            { x: 1, y: 0 }, { x: 0, y: 1 }, { x: 1, y: 1 }, { x: 1, y: -1 }
        ];
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                const player = board[row][col];
                if (!player) continue;
                for (let { x, y } of directions) {
                    let count = 1;
                    for (let step = 1; step < 4; step++) {
                        const r = row + step * y;
                        const c = col + step * x;
                        if (r >= 0 && r < this.boardSize && c >= 0 && c < this.boardSize && board[r][c] === player) {
                            count++;
                        } else {
                            break;
                        }
                    }
                    if (count === 4) return true;
                }
            }
        }
        return false;
    }

    // Draws the current state of the board
    drawBoard() {
        this.graphics.clear();
        this.graphics.fillStyle(0xbbada0, 0.9);
        this.graphics.fillRoundedRect(100, 100, 600, 600, 16);
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                if (this.board[row][col]) {
                    this.add.text(120 + col * 85, 120 + row * 85, this.board[row][col], {
                        fontSize: '32px', color: '#000'
                    }).setOrigin(0.5);
                }
            }
        }
    }

    // Resets the game to the initial state
    resetGame() {
        this.board = this.createBoard(this.boardSize, this.boardSize);
        this.currentPlayer = 'X';
        this.drawBoard();
    }
}
