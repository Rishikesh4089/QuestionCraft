import { ArrowRight } from "lucide-react";

import PaperCard from "./PaperCard";
import DashboardSectionHeader from "./DashboardSectionHeader";

interface Paper {
  id: string;
  title: string;
  subject: string;
  marks: number;
  bloom: string;
  date: string;
  status: "Draft" | "Final";
}

interface RecentPapersProps {
  papers: Paper[];

  onViewAll: () => void;

  onPreview: (id: string) => void;
  onDuplicate: (id: string) => void;
  onExport: (id: string) => void;
}

export default function RecentPapers({
  papers,
  onViewAll,
  onPreview,
  onDuplicate,
  onExport,
}: RecentPapersProps) {
  return (
    <section>

      <DashboardSectionHeader
        title="Recent Papers"
        action={
          <button
            onClick={onViewAll}
            className="
              flex
              items-center
              gap-2
              text-sm
              font-medium
              text-[var(--qc-primary)]
              hover:opacity-80
              transition-opacity
            "
          >
            View all
            <ArrowRight className="w-4 h-4" />
          </button>
        }
      />

      {papers.length === 0 ? (
        <div
          className="
            rounded-3xl
            border-2
            border-dashed
            border-[var(--qc-divider)]
            bg-white
            py-14
            text-center
          "
        >
          <h3
            className="
              text-lg
              font-semibold
              text-[var(--qc-text)]
            "
          >
            No papers yet
          </h3>

          <p
            className="
              mt-2
              text-sm
              text-[var(--qc-text-secondary)]
            "
          >
            Generate your first question paper to get started.
          </p>

        </div>
      ) : (

        <div
          className="
            grid
            grid-cols-1
            lg:grid-cols-3
            gap-5
          "
        >

          {papers.map((paper) => (
            <PaperCard
              key={paper.id}
              title={paper.title}
              subject={paper.subject}
              marks={paper.marks}
              bloom={paper.bloom}
              date={paper.date}
              status={paper.status}
              onPreview={() => onPreview(paper.id)}
              onDuplicate={() => onDuplicate(paper.id)}
              onExport={() => onExport(paper.id)}
            />
          ))}

        </div>

      )}

    </section>
  );
}