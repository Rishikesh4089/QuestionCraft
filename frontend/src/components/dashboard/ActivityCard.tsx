// src/components/dashboard/ActivityCard.tsx

import {
  Clock3,
  FileText,
  Upload,
  WandSparkles,
} from "lucide-react";

import DashboardCard from "./DashboardCard";

type ActivityType = "generate" | "upload" | "draft";

interface ActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  time: string;
}

interface ActivityCardProps {
  activities: ActivityItem[];
}

const activityIcons = {
  generate: WandSparkles,
  upload: Upload,
  draft: FileText,
};

export default function ActivityCard({
  activities,
}: ActivityCardProps) {
  return (
    <DashboardCard className="h-4/12">

      <div className="flex items-center justify-between mb-6">

        <div>
          <h3 className="text-lg font-semibold text-[var(--qc-text)]">
            Recent Activity
          </h3>

          <p className="text-sm text-[var(--qc-text-secondary)]">
            Your latest actions
          </p>
        </div>

        <Clock3 className="w-5 h-5 text-[var(--qc-primary)]" />

      </div>

      {activities.length === 0 ? (
        <div className="py-8 text-center">

          <p className="text-sm text-[var(--qc-text-secondary)]">
            No recent activity.
          </p>

        </div>
      ) : (
        <div className="space-y-5">

          {activities.map((activity, index) => {
            const Icon = activityIcons[activity.type];

            return (
              <div
                key={activity.id}
                className="flex items-start gap-4"
              >

                <div className="relative">

                  <div
                    className="
                      w-10
                      h-10
                      rounded-xl
                      bg-[var(--qc-primary)]/10
                      flex
                      items-center
                      justify-center
                      text-[var(--qc-primary)]
                    "
                  >
                    <Icon className="w-5 h-5" />
                  </div>

                  {index !== activities.length - 1 && (
                    <div
                      className="
                        absolute
                        left-1/2
                        top-10
                        -translate-x-1/2
                        w-px
                        h-7
                        bg-[var(--qc-divider)]
                      "
                    />
                  )}

                </div>

                <div className="flex-1">

                  <p className="text-sm font-medium text-[var(--qc-text)]">
                    {activity.title}
                  </p>

                  <p className="mt-1 text-xs text-[var(--qc-text-secondary)]">
                    {activity.time}
                  </p>

                </div>

              </div>
            );
          })}

        </div>
      )}

    </DashboardCard>
  );
}