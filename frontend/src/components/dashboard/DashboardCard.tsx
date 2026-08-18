// src/components/dashboard/DashboardCard.tsx

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface DashboardCardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

export default function DashboardCard({
  children,
  className,
  hover = false,
}: DashboardCardProps) {
  return (
    <div
      className={cn(
        "rounded-3xl",
        "bg-white",
        "border",
        "border-[var(--qc-divider)]",
        "shadow-sm",
        "p-6",
        "transition-all",
        hover &&
          "hover:-translate-y-1 hover:shadow-lg",
        className
      )}
    >
      {children}
    </div>
  );
}