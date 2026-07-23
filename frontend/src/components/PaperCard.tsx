// src/components/features/paper/PaperCard.tsx
import { Calendar, Eye, Pencil, Archive, Trash2, Download } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export interface Paper {
  id: string;
  user_id: string;
  paper_title: string;
  subject_name: string;
  total_marks: number;
  status: "Draft" | "Final" | "Archived";
  creation_date: string;
  paper_structure: any;
  pdf_url: string | null;
  docx_url?: string | null;
}

const statusVariant: Record<Paper["status"], "warning" | "success" | "default"> = {
  Draft:    "warning",
  Final:    "success",
  Archived: "default",
};

interface PaperCardProps {
  paper: Paper;
  onView: () => void;
  onEdit: () => void;
  onArchive: () => void;
  onDelete: () => void;
}

export default function PaperCard({ paper, onView, onEdit, onArchive, onDelete }: PaperCardProps) {
  const sections = paper.paper_structure?.paper?.sections ?? paper.paper_structure?.sections ?? [];
  const totalQuestions = sections.reduce((acc: number, s: any) => acc + (s.questions?.length ?? 0), 0);

  return (
    <div className="group bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 hover:shadow-md transition-all">
      <div className="flex items-start justify-between gap-4 mb-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-slate-900 truncate">{paper.paper_title}</h3>
            <Badge variant={statusVariant[paper.status]}>{paper.status}</Badge>
          </div>
          <div className="flex items-center flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">
            <span className="font-medium text-slate-700">{paper.subject_name}</span>
            <span>·</span>
            <span>{paper.total_marks} marks</span>
            {totalQuestions > 0 && (
              <>
                <span>·</span>
                <span>{totalQuestions} questions</span>
              </>
            )}
            <span>·</span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {new Date(paper.creation_date).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
            </span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <Button size="sm" variant="primary" icon={<Eye className="w-3.5 h-3.5" />} onClick={onView}>
          View
        </Button>
        <Button size="sm" variant="outline" icon={<Pencil className="w-3.5 h-3.5" />} onClick={onEdit}>
          Edit
        </Button>
        {paper.pdf_url && (
          <a
            href={paper.pdf_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 h-8 px-3 text-xs font-medium rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <Download className="w-3.5 h-3.5" /> PDF
          </a>
        )}
        {paper.status !== "Archived" && (
          <Button size="sm" variant="ghost" icon={<Archive className="w-3.5 h-3.5" />} onClick={onArchive} className="ml-auto">
            Archive
          </Button>
        )}
        <Button size="sm" variant="danger" icon={<Trash2 className="w-3.5 h-3.5" />} onClick={onDelete} className={paper.status === "Archived" ? "ml-auto" : ""}>
          Delete
        </Button>
      </div>
    </div>
  );
}