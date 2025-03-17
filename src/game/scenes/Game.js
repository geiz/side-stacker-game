import { EventBus } from '../EventBus';
import Phaser from 'phaser';
import { GameOver } from './GameOver';

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
    
        // Listen for game-over event and transition to GameOver scene
        EventBus.on('game-over', (winner) => {
            console.log('Game Over! Winner:', winner);
            //this.scene.start('GameOver', { winner }); // Pass winner data
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
            this.showWinnerPopup(this.currentPlayer);
        } else {
            this.currentPlayer = this.currentPlayer === 'X' ? 'O' : 'X';
            if (this.isAI && this.currentPlayer === 'O') {
                this.processAIMove();
            }
        }
    }

    // Handles AI's move decision
    processAIMove() {
        let move;
        if (this.aiDifficulty === 'easy') {
            move = this.getRandomMove();
        } else {
            move = this.getStrategicMove();
        }
        this.makeMove(move.row, move.side);
    }

    // Returns a random valid move for AI
    getRandomMove() {
        return {
            row: Math.floor(Math.random() * this.boardSize),
            side: Math.random() < 0.5 ? 'L' : 'R'
        };
    }

    // AI selects a move using a basic strategy
    getStrategicMove() {
        for (let row = 0; row < this.boardSize; row++) {
            for (let side of ['L', 'R']) {
                let testBoard = JSON.parse(JSON.stringify(this.board));
                let col = side === 'L' ? 0 : this.boardSize - 1;
                while (testBoard[row][col] !== null) {
                    col += side === 'L' ? 1 : -1;
                    if (col < 0 || col >= this.boardSize) break;
                }
                if (col >= 0 && col < this.boardSize) {
                    testBoard[row][col] = 'O';
                    if (this.checkWin(testBoard)) {
                        return { row, side };
                    }
                }
            }
        }
        return this.getRandomMove();
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

    // Draws grid lines and side indicators
drawGrid() {
    // Clear previous graphics
    this.graphics.clear();

    // Background color for the board
    this.graphics.fillStyle(0xbbada0, 0.9);
    this.graphics.fillRoundedRect(100, 100, 600, 600, 16);

    // Draw vertical grid lines
    for (let i = 1; i < this.boardSize; i++) {
        let x = 100 + (i * (600 / this.boardSize));
        this.graphics.lineStyle(2, 0x000000, 1);
        this.graphics.beginPath();
        this.graphics.moveTo(x, 100);
        this.graphics.lineTo(x, 700);
        this.graphics.strokePath();
    }

    // Draw horizontal grid lines
    for (let i = 1; i < this.boardSize; i++) {
        let y = 100 + (i * (600 / this.boardSize));
        this.graphics.lineStyle(2, 0x000000, 1);
        this.graphics.beginPath();
        this.graphics.moveTo(100, y);
        this.graphics.lineTo(700, y);
        this.graphics.strokePath();
    }
}

// Adds visual indicators for left and right side
drawSideIndicators() {
    // Left side indicator (Blue)
    this.graphics.fillStyle(0x0000FF, 0.2);
    this.graphics.fillRect(30, 100, 70, 600); // Left padding

    // Right side indicator (Red)
    this.graphics.fillStyle(0xFF0000, 0.2);
    this.graphics.fillRect(700, 100, 70, 600); // Right padding

    // Text Labels
    this.add.text(65, 80, 'LEFT', { fontSize: '20px', color: '#0000FF' }).setOrigin(0.5);
    this.add.text(735, 80, 'RIGHT', { fontSize: '20px', color: '#FF0000' }).setOrigin(0.5);
}


    // Draws the current state of the board
    drawBoard() {
        this.graphics.clear(); // Clears old graphics
        this.drawGrid(); // Draws grid lines
        this.drawSideIndicators(); // Draws side indicators
    
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                if (this.board[row][col]) {
                    this.add.text(120 + col * 85, 120 + row * 85, this.board[row][col], {
                        fontSize: '32px',
                        color: '#000'
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

    // Show winner popup
    showWinnerPopup(winner) {
        // Create a semi-transparent background
        const modalBackground = this.add.graphics();
        modalBackground.fillStyle(0x000000, 0.5); // Black with 50% opacity
        modalBackground.fillRect(0, 0, this.scale.width, this.scale.height);
        
        // Create a centered popup window
        const popup = this.add.graphics();
        popup.fillStyle(0xffffff, 1); // White background
        popup.fillRoundedRect(250, 200, 500, 300, 16); // Position, size, and rounded corners
    
        // Display winner text
        const winnerText = this.add.text(500, 250, `Winner: ${winner}`, {
            fontSize: '32px',
            color: '#000',
            fontFamily: 'Arial Black'
        }).setOrigin(0.5);
    
        // Create a "Try Again" button
        const tryAgainButton = this.add.text(500, 350, 'Play Again', {
            fontSize: '24px',
            color: '#ffffff',
            backgroundColor: '#ff0000',
            padding: { x: 10, y: 5 }
        })
        .setOrigin(0.5)
        .setInteractive()
        .on('pointerdown', () => {
            modalBackground.destroy();
            popup.destroy();
            winnerText.destroy();
            tryAgainButton.destroy();
            EventBus.emit('game-over', this);
        });
    
        // Add all elements to a Phaser Container for easier cleanup
        this.popupGroup = this.add.container(0, 0, [modalBackground, popup, winnerText, tryAgainButton]);
    }

    
}
