import { useEffect, useRef } from 'react';
import Phaser from 'phaser';
import { EventBus } from './EventBus';
import { Game } from './scenes/Game';

export const PhaserGame = ({ currentActiveScene }) => {
    const gameRef = useRef(null);

    useEffect(() => {
        if (!gameRef.current) {
            const config = {
                type: Phaser.AUTO,
                width: 800,
                height: 600,
                parent: 'game-container',
                backgroundColor: '#040218',
                scene: [Game],
                physics: {
                    default: 'arcade',
                    arcade: {
                        gravity: { y: 0 },
                        debug: true
                    }
                }
            };
            
            gameRef.current = new Phaser.Game(config);
        }

        const handleSceneReady = (scene) => {
            console.log('Game scene ready:', scene);
            if (currentActiveScene) {
                currentActiveScene(scene);
            }
        };

        EventBus.on('current-scene-ready', handleSceneReady);

        return () => {
            EventBus.off('current-scene-ready', handleSceneReady);
            if (gameRef.current) {
                gameRef.current.destroy(true);
                gameRef.current = null;
            }
        };
    }, [currentActiveScene]);

    return <div id="game-container" style={{ width: '800px', height: '600px', margin: 'auto', backgroundColor: 'black' }}></div>;
};

export default PhaserGame;
