import React from "react";

interface Props {
  totalMarks: number;
  onTotalMarksChange: (value: number) => void;
  onGenerate: (settings: any) => void | Promise<void>;
}



const PaperSettingsSection: React.FC<Props> = ({ totalMarks, onTotalMarksChange }) => (
  <div className="mb-6">
    <label className="block text-lg font-medium text-slate-700 mb-2">2. Total Marks</label>
    <input
      type="number"
      value={totalMarks}
      onChange={(e) => onTotalMarksChange(Number(e.target.value))}
      className="mt-1 block w-full px-3 py-2 border border-slate-300 rounded-md"
    />
  </div>
);

export default PaperSettingsSection;
