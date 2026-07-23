// src/components/dashboard/HeroActions.tsx

import {
  FileText,
  LayoutTemplate,
  BookOpen,
} from "lucide-react";

import ActionCard from "./ActionCard";

interface HeroActionsProps {
  userName: string;
  onGenerate: () => void;
  onTemplates: () => void;
  onQuestionBanks: () => void;
}

export default function HeroActions({
  userName,
  onGenerate,
  onTemplates,
  onQuestionBanks,
}: HeroActionsProps) {
  const greeting = () => {
    const hour = new Date().getHours();

    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <section>

      {/* Greeting */}

      <div className="mb-8">

        <h1
          className="
            text-4xl
            font-bold
            tracking-[-0.04em]
            text-[var(--qc-text)]
          "
        >
          {greeting()}, {userName} 👋
        </h1>

        <p
          className="
            mt-2
            text-lg
            text-[var(--qc-text-secondary)]
          "
        >
          What would you like to create today?
        </p>

      </div>

      {/* Actions */}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

        <ActionCard
          primary
          icon={<FileText className="w-6 h-6" />}
          title="Generate from Documents"
          description="Create AI-powered question papers from your uploaded teaching materials."
          onClick={onGenerate}
        />

        <ActionCard
          icon={<LayoutTemplate className="w-6 h-6" />}
          title="Use Template"
          description="Start with an existing assessment template and customise it."
          onClick={onTemplates}
        />

        <ActionCard
          icon={<BookOpen className="w-6 h-6" />}
          title="Question Bank"
          description="Create and manage reusable AI-powered question repositories."
          onClick={onQuestionBanks}
        />

      </div>

    </section>
  );
}