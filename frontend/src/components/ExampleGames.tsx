import React from 'react';
import type { ExampleScenario } from '../types/game';
import { exampleScenarios } from '../data/exampleScenarios';

interface ExampleGamesProps {
  onLoadScenario: (scenario: ExampleScenario) => void;
  loading: boolean;
}

export const ExampleGames: React.FC<ExampleGamesProps> = ({ onLoadScenario, loading }) => {
  return (
    <div className="bg-white rounded-xl shadow-md p-4">
      <h3 className="text-lg font-bold text-gray-800 mb-3">Example Endgames</h3>
      <div className="space-y-2">
        {exampleScenarios.map((scenario) => (
          <button
            key={scenario.id}
            onClick={() => onLoadScenario(scenario)}
            disabled={loading}
            className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <div className="font-semibold text-gray-800 text-sm">{scenario.title}</div>
            <div className="text-gray-500 text-xs mt-1">{scenario.description}</div>
            <div className="flex gap-3 mt-2 text-xs text-gray-400">
              <span>P: {scenario.northPositions.length}</span>
              <span>D: {scenario.southPositions.length}</span>
              <span>Turn: {scenario.startingPlayer === 'pangui' ? 'Pangui' : 'Pu Trewa'}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
