export interface PaperTemplate {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  total_marks: number;
  pattern_config: PatternConfig;
  unit_distribution: Record<string, number>;
  difficulty_distribution: DifficultyDistribution;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface PatternConfig {
  question_types: QuestionType[];
  sections?: Section[];
}

export interface QuestionType {
  id: string;
  type: string;
  marks_per_question: number;
  number_of_questions: number;
  total_marks: number;
}

export interface Section {
  id: string;
  name: string;
  question_types: string[];
}

export interface DifficultyDistribution {
  easy: number;
  medium: number;
  hard: number;
}

export interface GeneratedPaper {
  id: string;
  user_id: string;
  template_id?: string;
  title: string;
  subject?: string;
  paper_content: PaperContent;
  metadata: PaperMetadata;
  status: 'draft' | 'final' | 'archived';
  created_at: string;
  updated_at: string;
}

export interface PaperContent {
  questions: Question[];
  instructions?: string;
}

export interface Question {
  id: string;
  question_text: string;
  marks: number;
  difficulty: 'easy' | 'medium' | 'hard';
  unit: number;
  type: string;
  sub_questions?: Question[];
}

export interface PaperMetadata {
  source_files: string[];
  generation_params: Record<string, unknown>;
  generated_at: string;
}

export interface StudyMaterial {
  id: string;
  user_id: string;
  paper_id?: string;
  file_name: string;
  file_type: 'pdf' | 'image' | 'ppt' | 'text';
  file_url: string;
  file_size: number;
  unit_number?: number;
  uploaded_at: string;
}
