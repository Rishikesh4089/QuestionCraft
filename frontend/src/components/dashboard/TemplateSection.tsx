import { FileText, ArrowRight } from "lucide-react";

import DashboardCard from "./DashboardCard";
import DashboardSectionHeader from "./DashboardSectionHeader";

interface Template {
  id: string;
  name: string;
  description: string;
}

interface TemplateSectionProps {
  templates: Template[];
  onSelect: (id: string) => void;
  onBrowseAll?: () => void;
}

export default function TemplateSection({
  templates,
  onSelect,
  onBrowseAll,
}: TemplateSectionProps) {
  return (
    <section>
      <DashboardSectionHeader
        title="Templates"
        action={
          onBrowseAll && (
            <button
              onClick={onBrowseAll}
              className="flex items-center gap-2 text-sm font-medium text-[var(--qc-primary)] hover:opacity-80 transition-opacity"
            >
              Browse all
              <ArrowRight className="w-4 h-4" />
            </button>
          )
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        {templates.map((template) => (
          <button
            key={template.id}
            onClick={() => onSelect(template.id)}
            className="text-left"
          >
            <DashboardCard hover className="h-full">
              <div className="w-12 h-12 rounded-2xl bg-[var(--qc-primary)]/10 text-[var(--qc-primary)] flex items-center justify-center mb-5">
                <FileText className="w-6 h-6" />
              </div>

              <h3 className="text-lg font-semibold text-[var(--qc-text)]">
                {template.name}
              </h3>

              <p className="mt-2 text-sm leading-6 text-[var(--qc-text-secondary)]">
                {template.description}
              </p>
            </DashboardCard>
          </button>
        ))}
      </div>
    </section>
  );
}