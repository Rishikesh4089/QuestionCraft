import DashboardCard from "./DashboardCard";
import Button from "@/components/ui/Button";

interface CreditUsageCardProps {
  usedCredits: number;
  totalCredits: number;
  planName: string;
  onUpgrade?: () => void;
}

export default function CreditUsageCard({
  usedCredits,
  totalCredits,
  planName,
  onUpgrade,
}: CreditUsageCardProps) {
  const percentage =
    totalCredits === 0
      ? 0
      : Math.min((usedCredits / totalCredits) * 100, 100);

  const remaining = Math.max(totalCredits - usedCredits, 0);

  return (
    <DashboardCard className="h-4/12">
      <div className="flex flex-col h-full">

        <div>
          <p className="text-sm font-medium text-[var(--qc-text-secondary)]">
            Current Plan
          </p>

          <h3 className="mt-1 text-xl font-semibold text-[var(--qc-text)]">
            {planName}
          </h3>
        </div>

        <div className="mt-8">

          <div className="flex items-end justify-between">
            <div>
              <p className="text-4xl font-bold text-[var(--qc-text)]">
                {remaining}
              </p>

              <p className="text-sm text-[var(--qc-text-secondary)] mt-1">
                Credits Remaining
              </p>
            </div>

            <span className="text-sm font-medium text-[var(--qc-primary)]">
              {usedCredits}/{totalCredits}
            </span>
          </div>

          <div className="mt-5 h-3 rounded-full bg-[var(--qc-divider)] overflow-hidden">
            <div
              className="h-full rounded-full bg-[var(--qc-primary)] transition-all duration-500"
              style={{
                width: `${percentage}%`,
              }}
            />
          </div>

        </div>

        <div className="mt-8">
          <Button
            className="w-full"
            onClick={onUpgrade}
          >
            Upgrade Plan
          </Button>
        </div>

      </div>
    </DashboardCard>
  );
}