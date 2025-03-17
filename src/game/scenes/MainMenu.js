import { EventBus } from '../EventBus';
import { Scene } from 'phaser';

export class MainMenu extends Scene
{
    logoTween;

    constructor ()
    {
        super('MainMenu');
    }

    create() {
        this.add.image(512, 384, 'background');

        this.logo = this.add.image(512, 300, 'logo').setDepth(100);

        this.add.text(512, 460, 'Main Menu', {
            fontFamily: 'Arial Black', fontSize: 38, color: '#ffffff',
            stroke: '#000000', strokeThickness: 8,
            align: 'center'
        }).setDepth(100).setOrigin(0.5);

        const startButton = this.add.text(512, 550, 'Start Game', {
            fontFamily: 'Arial', fontSize: 32, color: '#ffffff',
            stroke: '#000000', strokeThickness: 4,
            backgroundColor: '#333',
            padding: { x: 10, y: 5 }
        }).setOrigin(0.5).setInteractive();

        startButton.on('pointerdown', () => {
            this.startGame();
        });

        startButton.on('pointerover', () => startButton.setBackgroundColor('#555'));
        startButton.on('pointerout', () => startButton.setBackgroundColor('#333'));

        EventBus.emit('current-scene-ready', this);
    }

    startGame() {
        if (this.logoTween) {
            this.logoTween.stop();
            this.logoTween = null;
        }

        this.scene.start('Game');
    }

    moveLogo(reactCallback) {
        if (this.logoTween) {
            if (this.logoTween.isPlaying()) {
                this.logoTween.pause();
            } else {
                this.logoTween.play();
            }
        } else {
            this.logoTween = this.tweens.add({
                targets: this.logo,
                x: { value: 750, duration: 3000, ease: 'Back.easeInOut' },
                y: { value: 80, duration: 1500, ease: 'Sine.easeOut' },
                yoyo: true,
                repeat: -1,
                onUpdate: () => {
                    if (reactCallback) {
                        reactCallback({
                            x: Math.floor(this.logo.x),
                            y: Math.floor(this.logo.y)
                        });
                    }
                }
            });
        }
    }
}
