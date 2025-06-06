import { useRef, useState, useEffect } from 'react';
import Phaser from 'phaser';
import { PhaserGame } from './game/PhaserGame';
import { EventBus } from './game/EventBus';


const App = () => {
    const [mode, setMode] = useState(null);
    const [difficulty, setDifficulty] = useState('easy');
    // The sprite can only be moved in the MainMenu Scene
    const [canMoveSprite, setCanMoveSprite] = useState(true);

    //  References to the PhaserGame component (game and scene are exposed)
    const phaserRef = useRef();
    const [spritePosition, setSpritePosition] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const handleGameOver = (winner) => {
            console.log('Game Over! Winner:', winner);
            setMode(null); // Reset mode to return to menu
        };

        EventBus.on('game-over', handleGameOver);
        return () => EventBus.off('game-over', handleGameOver);
    }, []);


    const changeScene = () => {

        const scene = phaserRef.current.scene;

        if (scene) {
            scene.changeScene();
        }
    }

    const moveSprite = () => {

        const scene = phaserRef.current.scene;

        if (scene && scene.scene.key === 'MainMenu') {
            // Get the update logo position
            scene.moveLogo(({ x, y }) => {

                setSpritePosition({ x, y });

            });
        }
    }

    const addSprite = () => {

        const scene = phaserRef.current.scene;

        if (scene) {
            // Add more stars
            const x = Phaser.Math.Between(64, scene.scale.width - 64);
            const y = Phaser.Math.Between(64, scene.scale.height - 64);

            //  `add.sprite` is a Phaser GameObjectFactory method and it returns a Sprite Game Object instance
            const star = scene.add.sprite(x, y, 'star');

            //  ... which you can then act upon. Here we create a Phaser Tween to fade the star sprite in and out.
            //  You could, of course, do this from within the Phaser Scene code, but this is just an example
            //  showing that Phaser objects and systems can be acted upon from outside of Phaser itself.
            scene.add.tween({
                targets: star,
                duration: 500 + Math.random() * 1000,
                alpha: 0,
                yoyo: true,
                repeat: -1
            });
        }
    }

    // Event emitted from the PhaserGame component
    const currentScene = (scene) => {

        setCanMoveSprite(scene.scene.key !== 'MainMenu');

    }

    const startGame = (selectedMode, selectedDifficulty) => {
        setMode(selectedMode);
        setDifficulty(selectedDifficulty);
        EventBus.emit('start-game', { mode: selectedMode, difficulty: selectedDifficulty });
    };

    return (
        <div>
            {!mode ? (
                <div>
                    <h1>Side Stacker Game</h1>
                    <button onClick={() => startGame('PvP', 'none')}>Play PvP</button>
                    <button onClick={() => startGame('AI', 'easy')}>Play AI (Easy)</button>
                    <button onClick={() => startGame('AI', 'hard')}>Play AI (Hard)</button>
                </div>
            ) : (
                <PhaserGame mode={mode} difficulty={difficulty} />
            )}
        </div>
    )
}

export default App
