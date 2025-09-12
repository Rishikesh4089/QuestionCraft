export interface Question {
  id: number;
  type: "EASY" | "MEDIUM" | "HARD";
  text: string;
  answer: string;
  marks: number;
}

export interface Paper {
  title: string;
  totalMarks: number;
  questions: Question[];
}

export interface Difficulty {
  easy: number;
  medium: number;
  hard: number;
}

export interface Unit {
  id: number;
  name: string;
  percentage: number;
}
