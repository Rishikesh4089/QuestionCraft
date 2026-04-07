import { useEffect, useState } from "react";
import {
  FileText,
  Calendar,
  Eye,
  Trash2,
  Archive,
  Filter,
  Pencil,
} from "lucide-react";
import { supabase } from "../lib/supabase";
import { useAuth } from "../contexts/AuthContext";
import PaperPreviewModal from "../components/PaperPreviewModal";
import CoolBlobEffect from "@/components/ui/cool-blob-effect";

interface Paper {
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

export default function PaperHistory() {
  const { user } = useAuth();
  const [filter, setFilter] = useState<"All" | "Draft" | "Final" | "Archived">("All");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  // ============================================================
  // 📦 Fetch all papers for logged-in user
  // ============================================================
  useEffect(() => {
    if (!user) return;
    const fetchPapers = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from("previous_papers")
        .select("*")
        .eq("user_id", user.id)
        .order("creation_date", { ascending: false });

      if (error) console.error("Error fetching papers:", error);
      else setPapers(data || []);
      setLoading(false);
    };

    fetchPapers();
  }, [user]);

  // ============================================================
  // 📑 Filter logic
  // ============================================================
  const filteredPapers =
    filter === "All"
      ? papers
      : papers.filter((p) => p.status.toLowerCase() === filter.toLowerCase());

  // ============================================================
  // ❌ Delete Paper
  // ============================================================
  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this paper?")) return;
    const { error } = await supabase.from("previous_papers").delete().eq("id", id);
    if (!error) setPapers(papers.filter((p) => p.id !== id));
  };

  // ============================================================
  // 🗂 Archive Paper
  // ============================================================
  const handleArchive = async (id: string) => {
    const { error } = await supabase
      .from("previous_papers")
      .update({ status: "Archived", archived_at: new Date() })
      .eq("id", id);
    if (!error)
      setPapers(
        papers.map((p) =>
          p.id === id ? { ...p, status: "Archived" } : p
        )
      );
  };

  return (
    <div className="relative flex-1 overflow-auto bg-slate-50 min-h-screen">
      {/* 🌈 Cool Blob Background */}
      <div className="absolute inset-0 z-0 opacity-80 pointer-events-none">
        <CoolBlobEffect />
      </div>

      {/* 📚 Main Content */}
      <div className="relative z-10 max-w-7xl mx-auto p-8">
        <div className="mb-8 text-center md:text-left">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Previous Papers</h1>
          <p className="text-slate-600">
            View and manage your generated question papers
          </p>
        </div>

        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-lg mb-6 border border-white/20">
          {/* Filter Bar */}
          <div className="p-4 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-slate-600" />
              <span className="font-medium text-slate-900">Filter by status:</span>
            </div>
            <div className="flex space-x-2">
              {["All", "Draft", "Final", "Archived"].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f as typeof filter)}
                  className={`px-4 py-2 rounded-lg transition-colors capitalize ${
                    filter === f
                      ? "bg-slate-800 text-white"
                      : "bg-slate-100 text-slate-700 hover:bg-slate-200"
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Paper List */}
          <div className="p-6">
            {loading ? (
              <div className="text-center py-12 text-slate-600">
                Loading papers...
              </div>
            ) : filteredPapers.length > 0 ? (
              <div className="space-y-4">
                {filteredPapers.map((paper) => (
                  <PaperCard
                    key={paper.id}
                    paper={paper}
                    onView={() => {
                      setSelectedPaper(paper);
                      setIsEditing(false);
                    }}
                    onEdit={() => {
                      setSelectedPaper(paper);
                      setIsEditing(true);
                    }}
                    onArchive={() => handleArchive(paper.id)}
                    onDelete={() => handleDelete(paper.id)}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600 text-lg">No papers found</p>
                <p className="text-slate-500 text-sm">
                  Try adjusting your filters or generate a new paper
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 🪟 View / Edit Modal */}
      {selectedPaper && (
        <PaperPreviewModal
          initialPaper={selectedPaper.paper_structure}
          pdfUrl={selectedPaper.pdf_url || undefined}
          docUrl={selectedPaper.docx_url || undefined}
          mode={isEditing ? "edit" : "view"}
          onClose={() => {
            setSelectedPaper(null);
            setIsEditing(false);
          }}
        />
      )}
    </div>
  );
}

function PaperCard({
  paper,
  onView,
  onEdit,
  onArchive,
  onDelete,
}: {
  paper: Paper;
  onView: () => void;
  onEdit: () => void;
  onArchive: () => void;
  onDelete: () => void;
}) {
  const statusColors = {
    Draft: "bg-orange-100 text-orange-700",
    Final: "bg-green-100 text-green-700",
    Archived: "bg-slate-100 text-slate-700",
  };

  return (
    <div className="border border-slate-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white/80 backdrop-blur-sm">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900 mb-1">
            {paper.paper_title}
          </h3>
          <div className="flex items-center flex-wrap space-x-4 text-sm text-slate-600">
            <span>{paper.subject_name}</span>
            <span>•</span>
            <span>{paper.total_marks} marks</span>
            <span>•</span>
            <div className="flex items-center space-x-1">
              <Calendar className="w-4 h-4" />
              <span>{new Date(paper.creation_date).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[paper.status]}`}
        >
          {paper.status}
        </span>
      </div>

      <div className="flex items-center flex-wrap gap-2">
        <button
          onClick={onView}
          className="flex items-center space-x-1 px-3 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors text-sm"
        >
          <Eye className="w-4 h-4" />
          <span>View</span>
        </button>

        <button
          onClick={onEdit}
          className="flex items-center space-x-1 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm"
        >
          <Pencil className="w-4 h-4" />
          <span>Edit</span>
        </button>

        {paper.status !== "Archived" && (
          <button
            onClick={onArchive}
            className="flex items-center space-x-1 px-3 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors text-sm"
          >
            <Archive className="w-4 h-4" />
            <span>Archive</span>
          </button>
        )}

        <button
          onClick={onDelete}
          className="flex items-center space-x-1 px-3 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm ml-auto"
        >
          <Trash2 className="w-4 h-4" />
          <span>Delete</span>
        </button>
      </div>
    </div>
  );
}
