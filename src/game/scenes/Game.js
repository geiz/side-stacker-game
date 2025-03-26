import { EventBus } from '../EventBus';
import Phaser from 'phaser';

const BOARD_SIZE = 420;
const OFFSET_X = 190; // Center board horizontally
const OFFSET_Y = 150; // Center board vertically


export class Game extends Phaser.Scene {
    constructor() {
        super('Game');
        this.boardSize = 7;
        this.board = this.createBoard(this.boardSize, this.boardSize);
        this.currentPlayer = 'X';
    }

    init(data) {
        this.isAI = data.mode === 'AI';
        this.aiDifficulty = data.difficulty || 'none';
        console.log(`Game Mode: ${data.mode}, Difficulty: ${data.difficulty}`);
    }

    // Preloads assets for the game
    preload() {
        this.addUI();
    }

    // Initializes the game scene
    create() {

        this.graphics = this.add.graphics(); // Initialize graphics

        this.drawBoard();

        console.log("is ai? ", this)

        this.setupEvents();
        EventBus.emit('current-scene-ready', this);
    }

    // Creates an empty game board
    createBoard(rows, cols) {
        return Array.from({ length: rows }, () => Array(cols).fill(null));
    }

    // Sets up event listeners
    setupEvents() {
        EventBus.on('start-game', ({ mode, difficulty }) => {
            console.log("Event received - Mode:", mode, "Difficulty:", difficulty); // Debugging
            this.isAI = mode === 'AI';
            this.aiDifficulty = difficulty;

            console
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
        const cellSize = BOARD_SIZE / this.boardSize;

        const row = Math.floor((pointer.y - OFFSET_Y) / cellSize);
        const side = pointer.x < OFFSET_X + BOARD_SIZE / 2 ? 'L' : 'R';

        // Ensure row index is within valid bounds
        if (row >= 0 && row < this.boardSize) {
            this.makeMove(row, side);
        } else {
            console.warn("Invalid row selection:", row);
        }
    }

    // Processes a player's move
    makeMove(row, side) {
        let col = side === 'L' ? 0 : this.boardSize - 1;

        // Find the next available space in the selected row
        while (this.board[row][col] !== null) {
            col += side === 'L' ? 1 : -1;
            if (col < 0 || col >= this.boardSize) return; // Move is invalid
        }

        // Place player's move
        this.board[row][col] = this.currentPlayer;
        this.drawBoard();

        // Check for a winner
        if (this.checkWin()) {
            this.showWinnerPopup(this.currentPlayer);
            return;
        }

        // Switch turn
        this.currentPlayer = this.currentPlayer === 'X' ? 'O' : 'X';

        // AI move if it's enabled and AI's turn
        if (this.isAI && this.currentPlayer === 'O') {
            this.time.delayedCall(25, () => this.processAIMove()); // Delay for better UX
        }
    }

    // Return the current state of the board as a formatted string, matching the structure expected by the AI
    getBoardState() {
        let boardString = "";
    
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                boardString += this.board[row][col] ? this.board[row][col] : "_";
            }
            if (row < this.boardSize - 1) boardString += " | "; // Separate rows with a delimiter
        }
    
        return boardString;
    }

    // Handles AI's move decision by calling backend.
    async processAIMove() {
        const boardState = this.getBoardState(); // Convert board to a string
    
        try {
            const response = await fetch('http://127.0.0.1:5001/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board: boardState, difficulty: this.aiDifficulty }) // Send difficulty level
            });
    
            const data = await response.json();
            console.log("data: ", data)
    
            if (data.move) {

                // Data should already be formatted from backend.
                const [row, side] = data.move;
                this.makeMove(row, side);
            } else {
                console.error('Invalid AI move response:', data);
            }
        } catch (error) {
            console.error('Error fetching AI move:', error);
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

    // Adds UI elements to the game
    addUI() {
        this.cameras.main.setBackgroundColor(0x87CEEB);

        this.add.text(400, 25, 'Side Stacker Game', {
            fontFamily: 'Arial Black', fontSize: 32, color: '#ffffff',
            stroke: '#000000', strokeThickness: 6,
            align: 'center'
        }).setOrigin(0.5);

        this.graphics = this.add.graphics();
        this.graphics.fillStyle(0xbbada0, 0.9);
        this.graphics.fillRoundedRect(100, 100, 600, 600, 16);
        this.input.on('pointerdown', this.handleClick, this);
    }

    // Draws grid lines and side indicators
    drawGrid() {
        this.graphics.clear();
    
        // Background color for the board
        this.graphics.fillStyle(0xbbada0, 0.9);
        this.graphics.fillRoundedRect(OFFSET_X, OFFSET_Y, BOARD_SIZE, BOARD_SIZE, 16);
    
        const cellSize = BOARD_SIZE / this.boardSize;
    
        // Draw vertical grid lines
        for (let i = 1; i < this.boardSize; i++) {
            let x = OFFSET_X + i * cellSize;
            this.graphics.lineStyle(2, 0x000000, 1);
            this.graphics.beginPath();
            this.graphics.moveTo(x, OFFSET_Y);
            this.graphics.lineTo(x, OFFSET_Y + BOARD_SIZE);
            this.graphics.strokePath();
        }
    
        // Draw horizontal grid lines
        for (let i = 1; i < this.boardSize; i++) {
            let y = OFFSET_Y + i * cellSize;
            this.graphics.lineStyle(2, 0x000000, 1);
            this.graphics.beginPath();
            this.graphics.moveTo(OFFSET_X, y);
            this.graphics.lineTo(OFFSET_X + BOARD_SIZE, y);
            this.graphics.strokePath();
        }
    }
    
    // Adds visual indicators for left and right side
    drawSideIndicators() {
        this.graphics.fillStyle(0x0000FF, 0.2);
        this.graphics.fillRect(OFFSET_X - 50, OFFSET_Y, 50, BOARD_SIZE); // Left padding
    
        this.graphics.fillStyle(0xFF0000, 0.2);
        this.graphics.fillRect(OFFSET_X + BOARD_SIZE, OFFSET_Y, 50, BOARD_SIZE); // Right padding
    
        // Text Labels
        this.add.text(OFFSET_X - 25, OFFSET_Y - 20, 'LEFT', { fontSize: '18px', color: '#0000FF' }).setOrigin(0.5);
        this.add.text(OFFSET_X + BOARD_SIZE + 25, OFFSET_Y - 20, 'RIGHT', { fontSize: '18px', color: '#FF0000' }).setOrigin(0.5);
    }
    
    // Draws the current state of the board
    drawBoard() {
        this.graphics.clear();
        this.drawGrid();
        this.drawSideIndicators();
    
        const cellSize = BOARD_SIZE / this.boardSize;
    
        for (let row = 0; row < this.boardSize; row++) {
            for (let col = 0; col < this.boardSize; col++) {
                if (this.board[row][col]) {
                    this.add.text(
                        OFFSET_X + (col + 0.5) * cellSize, 
                        OFFSET_Y + (row + 0.5) * cellSize, 
                        this.board[row][col], 
                        { fontSize: '28px', color: '#000' }
                    ).setOrigin(0.5);
                }
            }
        }
    }

    // Resets the game to the initial state
    resetGame() {
        this.board = this.createBoard(this.boardSize, this.boardSize);
        this.currentPlayer = 'X';
        this.drawBoard();

        if (this.isAI && this.currentPlayer === 'O') {
            this.processAIMove(); // AI plays first if it's 'O'
        }
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
