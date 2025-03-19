import { useEffect, useRef, useState } from 'react';
import Phaser from 'phaser';
import { EventBus } from './EventBus';
import { Game } from './scenes/Game';

export const PhaserGame = (props) => {
    const gameRef = useRef(null);

    const [mode, setMode] = useState(null);
    const [difficulty, setDifficulty] = useState('easy');


    useEffect(() => {
        setMode(props.mode);
        setDifficulty(props.difficulty);

        console.log("this: ", props)
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

            // Passes props
            gameRef.current.scene.start('Game', { mode, difficulty })
        }

        const handleSceneReady = (scene) => {
            console.log('Game scene ready:', scene);
            if (props.currentActiveScene) {
                props.currentActiveScene(scene);
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


    }, [mode, difficulty, props.currentActiveScene]);

    return <div id="game-container" style={{ width: '800px', height: '600px', margin: 'auto', backgroundColor: 'black' }}></div>;
};

export default PhaserGame;
