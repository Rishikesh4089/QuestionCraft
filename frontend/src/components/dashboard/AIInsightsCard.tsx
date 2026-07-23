import {
  Brain,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";

import DashboardCard from "./DashboardCard";

interface AIInsightsCardProps {
  bloomCoverage: number;
  averageDifficulty: string;
  suggestions: string[];
}

export default function AIInsightsCard({
  bloomCoverage,
  averageDifficulty,
  suggestions,
}: AIInsightsCardProps) {
  return (
    <DashboardCard className="h-5/12">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-11 h-11 rounded-xl bg-[var(--qc-primary)]/10 flex items-center justify-center text-[var(--qc-primary)]">
          <Brain className="w-5 h-5" />
        </div>

        <div>
          <h3 className="text-lg font-semibold text-[var(--qc-text)]">
            AI Insights
          </h3>

          <p className="text-sm text-[var(--qc-text-secondary)]">
            Your recent generation statistics
          </p>
        </div>
      </div>

      <div className="space-y-5">

        <div className="flex items-center justify-between">
          <span className="text-sm text-[var(--qc-text-secondary)]">
            Bloom Coverage
          </span>

          <span className="font-semibold text-[var(--qc-text)]">
            {bloomCoverage}%
          </span>
        </div>

        <div className="h-2 rounded-full bg-[var(--qc-divider)] overflow-hidden">
          <div
            className="h-full rounded-full bg-[var(--qc-primary)] transition-all"
            style={{
              width: `${bloomCoverage}%`,
            }}
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-[var(--qc-text-secondary)]">
            Avg. Difficulty
          </span>

          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-[var(--qc-primary)]" />

            <span className="font-semibold text-[var(--qc-text)]">
              {averageDifficulty}
            </span>
          </div>
        </div>

        <div className="pt-5 border-t border-[var(--qc-divider)]">

          <div className="flex items-center gap-2 mb-3">
            <AlertTriangle className="w-4 h-4 text-[var(--qc-primary)]" />

            <span className="text-sm font-medium text-[var(--qc-text)]">
              Suggestions
            </span>
          </div>

          <ul className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <li
                key={index}
                className="text-sm leading-6 text-[var(--qc-text-secondary)]"
              >
                • {suggestion}
              </li>
            ))}
          </ul>

        </div>

      </div>
    </DashboardCard>
  );
}