import type { ExampleScenario } from '../types/game';

export const exampleScenarios: ExampleScenario[] = [
  {
    id: 'final-capture',
    title: 'The Final Capture',
    description: 'South has only 5 tokens. One capture wins the game for Pangui!',
    northPositions: [[2, 4]],
    southPositions: [[2, 5], [1, 6], [3, 6], [0, 7], [4, 7]],
    startingPlayer: 'pangui',
  },
  {
    id: 'closing-the-net',
    title: 'Closing the Net',
    description: 'The pack is closing in. Can South seal the trap before Pangui escapes?',
    northPositions: [[2, 4]],
    southPositions: [[2, 3], [3, 4], [2, 5], [2, 2], [4, 4], [2, 6], [1, 5], [0, 4], [1, 6], [3, 6]],
    startingPlayer: 'pu trewa',
  },
  {
    id: 'fork-attack',
    title: 'Fork Attack',
    description: 'Multiple captures available. Choose wisely — not all paths lead to victory!',
    northPositions: [[2, 4]],
    southPositions: [[1, 4], [3, 4], [2, 5], [0, 6], [1, 7], [3, 7]],
    startingPlayer: 'pangui',
  },
  {
    id: 'narrow-escape',
    title: 'Narrow Escape',
    description: 'Almost surrounded! Pangui must find the way out before the trap closes.',
    northPositions: [[2, 5]],
    southPositions: [[1, 4], [2, 4], [3, 4], [3, 5], [1, 6], [2, 6], [3, 6], [0, 5]],
    startingPlayer: 'pangui',
  },
  {
    id: 'deep-in-enemy-lines',
    title: 'Deep in Enemy Lines',
    description: 'Pangui is deep in South territory, surrounded but with capture opportunities.',
    northPositions: [[2, 6]],
    southPositions: [[1, 5], [2, 5], [3, 5], [1, 6], [3, 6], [1, 7], [2, 7], [3, 7], [4, 5]],
    startingPlayer: 'pangui',
  },
];
