import React from "react";
import type { Difficulty } from "../types/paper";

interface Props {
  difficulty: Difficulty;
  onDifficultyChange: (level: keyof Difficulty, value: number) => void;
}

const DifficultySplitSection: React.FC<Props> = ({ difficulty, onDifficultyChange }) => (
  <div className="mb-6">
    <label className="block text-lg font-medium text-slate-700 mb-2">3. Difficulty Split (%)</label>
    <div className="grid grid-cols-3 gap-4 mt-2">
      {Object.keys(difficulty).map((level) => (
        <div key={level}>
          <label className="block text-sm font-medium capitalize">{level}</label>
          <input
            type="number"
            value={difficulty[level as keyof Difficulty]}
            onChange={(e) => onDifficultyChange(level as keyof Difficulty, Number(e.target.value))}
            className="mt-1 block w-full px-3 py-2 border border-slate-300 rounded-md"
          />
        </div>
      ))}
    </div>
  </div>
);

export default DifficultySplitSection;
