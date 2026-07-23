// src/components/dashboard/PaperCard.tsx

import {
  Calendar,
  Eye,
  Copy,
  Download,
} from "lucide-react";

import DashboardCard from "./DashboardCard";
import Button from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

interface PaperCardProps {
  title: string;
  subject: string;
  marks: number;
  bloom: string;
  date: string;
  status: "Draft" | "Final";

  onPreview: () => void;
  onDuplicate: () => void;
  onExport: () => void;
}

export default function PaperCard({
  title,
  subject,
  marks,
  bloom,
  date,
  status,
  onPreview,
  onDuplicate,
  onExport,
}: PaperCardProps) {
  return (
    <DashboardCard
      hover
      className="flex flex-col justify-between h-full"
    >
      {/* Header */}

      <div>

        <div className="flex items-start justify-between">

          <div>

            <p
              className="
                text-xs
                font-medium
                uppercase
                tracking-wider
                text-[var(--qc-primary)]
              "
            >
              {subject}
            </p>

            <h3
              className="
                mt-2
                text-lg
                font-semibold
                text-[var(--qc-text)]
              "
            >
              {title}
            </h3>

          </div>

          <Badge
            variant={
              status === "Final"
                ? "success"
                : "warning"
            }
          >
            {status}
          </Badge>

        </div>

        {/* Metadata */}

        <div className="mt-6 space-y-3">

          <div className="flex justify-between">

            <span className="text-sm text-[var(--qc-text-secondary)]">
              Marks
            </span>

            <span className="font-medium">
              {marks}
            </span>

          </div>

          <div className="flex justify-between">

            <span className="text-sm text-[var(--qc-text-secondary)]">
              Bloom
            </span>

            <span className="font-medium">
              {bloom}
            </span>

          </div>

          <div className="flex items-center gap-2 text-sm text-[var(--qc-text-secondary)]">

            <Calendar className="w-4 h-4" />

            {date}

          </div>

        </div>

      </div>

      {/* Footer */}

      <div className="flex gap-2 mt-8">

        <Button
          size="sm"
          variant="ghost"
          leftIcon={<Eye className="w-4 h-4" />}
          onClick={onPreview}
        >
          Preview
        </Button>

        <Button
          size="sm"
          variant="ghost"
          leftIcon={<Copy className="w-4 h-4" />}
          onClick={onDuplicate}
        >
          Duplicate
        </Button>

        <Button
          size="sm"
          leftIcon={<Download className="w-4 h-4" />}
          onClick={onExport}
        >
          Export
        </Button>

      </div>

    </DashboardCard>
  );
}