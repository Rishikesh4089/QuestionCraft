import { ReactNode } from "react";
import DashboardCard from "./DashboardCard";

interface ActionCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  onClick: () => void;
  primary?: boolean;
}

export default function ActionCard({
  icon,
  title,
  description,
  onClick,
  primary = false,
}: ActionCardProps) {
  return (
    <button
      onClick={onClick}
      className="w-full text-left"
    >
      <DashboardCard
        hover
        className={`
          h-full
          ${
            primary
              ? "border-[var(--qc-primary)] bg-orange-50/40"
              : ""
          }
        `}
      >
        <div className="space-y-5">

          <div
            className="
              w-12
              h-12
              rounded-2xl
              flex
              items-center
              justify-center
              bg-[var(--qc-primary)]/10
              text-[var(--qc-primary)]
            "
          >
            {icon}
          </div>

          <div>

            <h3
              className="
                text-lg
                font-semibold
                text-[var(--qc-text)]
                mb-1
              "
            >
              {title}
            </h3>

            <p
              className="
                text-sm
                leading-6
                text-[var(--qc-text-secondary)]
              "
            >
              {description}
            </p>

          </div>

        </div>
      </DashboardCard>
    </button>
  );
}