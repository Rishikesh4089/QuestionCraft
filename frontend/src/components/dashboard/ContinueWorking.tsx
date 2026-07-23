import { Clock, ArrowRight } from "lucide-react";

import DashboardCard from "./DashboardCard";
import DashboardSectionHeader from "./DashboardSectionHeader";
import Button from "@/components/ui/Button";

interface DraftPaper {
  id: string;
  title: string;
  progress: number;
  updatedAt: string;
}

interface ContinueWorkingProps {
  drafts: DraftPaper[];
  onResume: (id: string) => void;
  onViewAll?: () => void;
}

export default function ContinueWorking({
  drafts,
  onResume,
  onViewAll,
}: ContinueWorkingProps) {
  if (drafts.length === 0) return null;

  return (
    <section>
      <DashboardSectionHeader
        title="Continue Working"
        action={
          onViewAll && (
            <button
              onClick={onViewAll}
              className="flex items-center gap-2 text-sm font-medium text-[var(--qc-primary)] hover:opacity-80 transition-opacity"
            >
              View all
              <ArrowRight className="w-4 h-4" />
            </button>
          )
        }
      />

      <div className="space-y-4">
        {drafts.map((draft) => (
          <DashboardCard
            key={draft.id}
            hover
            className="flex items-center justify-between"
          >
            <div className="flex-1">
              <h3 className="font-semibold text-[var(--qc-text)]">
                {draft.title}
              </h3>

              <div className="flex items-center gap-2 mt-2 text-sm text-[var(--qc-text-secondary)]">
                <Clock className="w-4 h-4" />
                Updated {draft.updatedAt}
              </div>

              <div className="mt-4">
                <div className="h-2 rounded-full bg-[var(--qc-divider)] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[var(--qc-primary)] transition-all"
                    style={{ width: `${draft.progress}%` }}
                  />
                </div>

                <p className="mt-2 text-xs text-[var(--qc-text-secondary)]">
                  {draft.progress}% Complete
                </p>
              </div>
            </div>

            <div className="ml-6">
              <Button onClick={() => onResume(draft.id)}>
                Resume
              </Button>
            </div>
          </DashboardCard>
        ))}
      </div>
    </section>
  );
}