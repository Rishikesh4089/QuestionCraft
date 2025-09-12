import type { Difficulty, Unit, Paper } from "../types/paper";

export const generateMockPaper = async (
  files: File[],
  totalMarks: number,
  difficulty: Difficulty,
  units: Unit[]
): Promise<Paper> => {
  console.log("Generating paper with config:", { files, totalMarks, difficulty, units });

  await new Promise((resolve) => setTimeout(resolve, 2000)); // simulate delay

  return {
    title: "Midterm Examination - Subject Name",
    totalMarks,
    questions: [
      {
        id: 1,
        type: "EASY",
        text: "What is the primary function of a hash table?",
        answer: "A hash table stores key-value pairs efficiently using a hash function.",
        marks: 5,
      },
      {
        id: 2,
        type: "MEDIUM",
        text: "Explain supervised vs unsupervised learning.",
        answer: "Supervised uses labeled data, unsupervised finds patterns in unlabeled data.",
        marks: 10,
      },
      {
        id: 3,
        type: "HARD",
        text: "Describe a diagram-based TCP/IP model question scenario.",
        answer: "Show a TCP/IP diagram with missing layers, ask students to fix and explain encapsulation.",
        marks: 15,
      },
      {
        id: 4,
        type: "EASY",
        text: "Define 'API'.",
        answer: "API is an Application Programming Interface for communication between software apps.",
        marks: 5,
      },
    ],
  };
};
