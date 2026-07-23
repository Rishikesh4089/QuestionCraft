import { ReactNode } from "react";

interface DashboardSectionHeaderProps {
  title: string;
  action?: ReactNode;
}

export default function DashboardSectionHeader({
  title,
  action,
}: DashboardSectionHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-5">
      <h2
        className="
          text-xl
          font-semibold
          tracking-[-0.02em]
          text-[var(--qc-text)]
        "
      >
        {title}
      </h2>

      {action}
    </div>
  );
}