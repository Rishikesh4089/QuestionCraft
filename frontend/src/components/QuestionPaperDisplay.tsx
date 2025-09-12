import React from "react";
import type { Paper } from "../types/paper";

interface Props {
  paper: Paper;
}

const QuestionPaperDisplay: React.FC<Props> = ({ paper }) => (
  <div className="w-full h-full p-4 overflow-y-auto bg-slate-50 rounded-lg">
    <h3 className="text-xl font-bold text-center mb-2">{paper.title}</h3>
    <div className="flex justify-between text-sm font-semibold mb-6 border-b pb-2">
      <span>Total Marks: {paper.totalMarks}</span>
      <span>Time: 3 Hours</span>
    </div>
    {paper.questions.map((q, i) => (
      <div key={q.id} className="mb-4">
        <p className="font-semibold">
          Q{i + 1}. {q.text} <span className="font-bold text-slate-700">[{q.marks}]</span>
        </p>
        <div className="mt-2 pl-4 border-l-2 border-blue-200">
          <p className="text-sm font-medium">Model Answer:</p>
          <p className="text-sm">{q.answer}</p>
        </div>
      </div>
    ))}
  </div>
);

export default QuestionPaperDisplay;
