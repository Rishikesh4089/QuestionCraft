import React from "react";
import type { Unit } from "../types/paper";

interface Props {
  units: Unit[];
  onUnitChange: (id: number, field: keyof Unit, value: string | number) => void;
  onAddUnit: () => void;
  onRemoveUnit: (id: number) => void;
}

const UnitSplitSection: React.FC<Props> = ({ units, onUnitChange, onAddUnit, onRemoveUnit }) => (
  <div>
    <label className="block text-lg font-medium text-slate-700 mb-2">4. Unit/Chapter Split (%)</label>
    <div className="space-y-3 mt-2">
      {units.map((unit) => (
        <div key={unit.id} className="flex gap-2">
          <input
            type="text"
            value={unit.name}
            onChange={(e) => onUnitChange(unit.id, "name", e.target.value)}
            className="flex-grow px-3 py-2 border border-slate-300 rounded-md"
          />
          <input
            type="number"
            value={unit.percentage}
            onChange={(e) => onUnitChange(unit.id, "percentage", Number(e.target.value))}
            className="w-20 px-3 py-2 border border-slate-300 rounded-md"
          />
          <button
            onClick={() => onRemoveUnit(unit.id)}
            disabled={units.length <= 1}
            className="text-red-500 hover:text-red-700"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
    <button onClick={onAddUnit} className="mt-3 text-sm text-blue-600">
      + Add Unit
    </button>
  </div>
);

export default UnitSplitSection;
