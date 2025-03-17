import { EventBus } from '../EventBus';
import { Scene } from 'phaser';

export class GameOver extends Scene {
    constructor() {
        super('GameOver');
        console.log("Loaded GameOver")
    }

    // Get the winner from the previous scene
    init(data) {
        this.winner = data?.winner || 'Unknown';
    }

    create() {
        this.cameras.main.setBackgroundColor(0xff0000);

        // Background Image
        this.add.image(512, 384, 'background').setAlpha(0.5);

        // Game Over Text
        this.add.text(512, 250, 'Game Over', {
            fontFamily: 'Arial Black', fontSize: 64, color: '#ffffff',
            stroke: '#000000', strokeThickness: 8,
            align: 'center'
        }).setOrigin(0.5);

        // Display the Winner
        this.add.text(512, 350, `Winner: ${this.winner}`, {
            fontFamily: 'Arial', fontSize: 32, color: '#ffffff',
            stroke: '#000000', strokeThickness: 4,
            align: 'center'
        }).setOrigin(0.5);

        // Button to go back to the Main Menu
        const backButton = this.add.text(512, 450, 'Main Menu', {
            fontFamily: 'Arial', fontSize: 32, color: '#ffffff',
            backgroundColor: '#0000ff',
            padding: { x: 10, y: 5 },
            align: 'center'
        }).setOrigin(0.5).setInteractive();

        // Handle clicking the button
        backButton.on('pointerdown', () => {
            this.scene.stop('GameOver');
            this.scene.start('MainMenu');
        });

        // Hover effect
        backButton.on('pointerover', () => {
            backButton.setBackgroundColor('#555');
        });

        backButton.on('pointerout', () => {
            backButton.setBackgroundColor('#333');
        });

        EventBus.emit('current-scene-ready', this);
    }
}
