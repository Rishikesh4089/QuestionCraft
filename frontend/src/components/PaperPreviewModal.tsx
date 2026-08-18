// src/components/features/paper/PaperPreviewModal.tsx
import { useState } from "react";
import { X, Download, RefreshCw, Trash2, Save, Edit3, FileText, Code } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { Badge } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import { cn } from "@/lib/utils";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

type Tab = "preview" | "json" | "edit";

interface PaperPreviewModalProps {
  initialPaper: any;
  pdfUrl?: string;
  docUrl?: string;
  mode?: "view" | "edit";
  onClose: () => void;
}

export default function PaperPreviewModal({
  initialPaper, pdfUrl, docUrl, mode = "view", onClose,
}: PaperPreviewModalProps) {
  const [tab, setTab] = useState<Tab>(mode === "edit" ? "edit" : "preview");
  const [editablePaper, setEditablePaper] = useState<any>(initialPaper);
  const [saving, setSaving] = useState(false);
  const [loadingSection, setLoadingSection] = useState<string | null>(null);
  const [loadingQuestion, setLoadingQuestion] = useState<string | null>(null);

  const paper = editablePaper?.paper ?? editablePaper;
  const sections: any[] = paper?.sections ?? [];

  // ── Regenerate section ────────────────────────────────────────────────────────
  const regenerateSection = async (section: any) => {
    setLoadingSection(section.section);
    try {
      const res = await fetch(`${API_BASE_URL}/regenerate-section/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: paper.subject,
          section: section.section,
          question_type: section.question_type,
          questions: section.questions,
          marks_each: section.questions?.[0]?.marks ?? 5,
          index_key: editablePaper?.index_key,
        }),
      });
      if (!res.ok) throw new Error("Failed");
      const data = await res.json();
      const newSection = data.section ?? data;
      setEditablePaper((prev: any) => {
        const p = prev?.paper ?? prev;
        const updated = { ...p, sections: p.sections.map((s: any) => s.section === section.section ? newSection : s) };
        return prev?.paper ? { ...prev, paper: updated } : updated;
      });
    } catch {
      alert("❌ Failed to regenerate section");
    } finally {
      setLoadingSection(null);
    }
  };

  // ── Regenerate question ───────────────────────────────────────────────────────
  const regenerateQuestion = async (section: any, qIdx: number) => {
    const key = `${section.section}-${qIdx}`;
    setLoadingQuestion(key);
    try {
      const res = await fetch(`${API_BASE_URL}/regenerate-question/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: paper.subject,
          section: section.section,
          question_type: section.question_type,
          topic: section.questions[qIdx]?.topic ?? "General",
          marks: section.questions[qIdx]?.marks,
          previous_questions: section.questions.map((q: any) => q.text),
          index_key: editablePaper?.index_key,
        }),
      });
      const data = await res.json();
      if (data.success && data.new_question) {
        setEditablePaper((prev: any) => {
          const p = prev?.paper ?? prev;
          const updated = {
            ...p, sections: p.sections.map((s: any) => s.section !== section.section ? s : {
              ...s, questions: s.questions.map((q: any, i: number) => i === qIdx ? data.new_question : q),
            }),
          };
          return prev?.paper ? { ...prev, paper: updated } : updated;
        });
      }
    } catch {
      alert("❌ Regeneration failed");
    } finally {
      setLoadingQuestion(null);
    }
  };

  // ── Delete section ─────────────────────────────────────────────────────────────
  const deleteSection = (sectionName: string) => {
    setEditablePaper((prev: any) => {
      const p = prev?.paper ?? prev;
      const updated = { ...p, sections: p.sections.filter((s: any) => s.section !== sectionName) };
      return prev?.paper ? { ...prev, paper: updated } : updated;
    });
  };

  // ── Save final ─────────────────────────────────────────────────────────────────
  const saveFinalPaper = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from("previous_papers")
        .update({ status: "Final", paper_structure: editablePaper, updated_at: new Date().toISOString() })
        .eq("subject_name", paper?.subject_name ?? paper?.subject);
      if (error) throw error;
      alert("✅ Paper saved as Final!");
      setTab("preview");
    } catch (err: any) {
      alert("❌ Failed to save: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl h-[92vh] flex flex-col overflow-hidden">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50 rounded-t-2xl">
          <div>
            <h2 className="text-base font-semibold text-slate-900">{paper?.subject ?? "Question Paper"}</h2>
            <p className="text-xs text-slate-500">{paper?.exam_name} · {paper?.total_marks} marks</p>
          </div>
          <div className="flex items-center gap-2">
            {tab === "edit" ? (
              <Button size="sm" loading={saving} leftIcon={<Save className="w-3.5 h-3.5" />} onClick={saveFinalPaper}>
                Save Final
              </Button>
            ) : (
              <Button size="sm" variant="outline" leftIcon={<Edit3 className="w-3.5 h-3.5" />} onClick={() => setTab("edit")}>
                Edit Paper
              </Button>
            )}
            <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-200 px-6 bg-white">
          {(["preview", "json", "edit"] as Tab[]).map((t) => {
            const labels: Record<Tab, string> = { preview: "PDF Preview", json: "JSON", edit: "Edit Mode" };
            const icons: Record<Tab, React.ReactNode> = {
              preview: <FileText className="w-3.5 h-3.5" />,
              json: <Code className="w-3.5 h-3.5" />,
              edit: <Edit3 className="w-3.5 h-3.5" />,
            };
            return (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={cn(
                  "flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors",
                  tab === t
                    ? "border-slate-900 text-slate-900"
                    : "border-transparent text-slate-500 hover:text-slate-700",
                )}
              >
                {icons[t]} {labels[t]}
              </button>
            );
          })}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto bg-slate-50">
          {tab === "preview" && (
            pdfUrl
              ? <iframe src={pdfUrl} className="w-full h-full" title="Paper PDF" />
              : <div className="flex items-center justify-center h-full text-slate-500 text-sm">No PDF available</div>
          )}

          {tab === "json" && (
            <pre className="text-xs text-slate-800 font-mono p-6 overflow-auto h-full leading-relaxed">
              {JSON.stringify(editablePaper, null, 2)}
            </pre>
          )}

          {tab === "edit" && (
            <div className="p-6 space-y-4">
              {sections.map((section) => (
                <div key={section.section} className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                  {/* Section header */}
                  <div className="flex items-center justify-between px-5 py-3 bg-slate-50 border-b border-slate-200">
                    <div className="flex items-center gap-2">
                      <span className="w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-bold flex items-center justify-center">
                        {section.section}
                      </span>
                      <span className="text-sm font-semibold text-slate-800">{section.question_type}</span>
                      <Badge variant="default">{section.questions?.length ?? 0} questions</Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm" variant="outline"
                        loading={loadingSection === section.section}
                        leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
                        onClick={() => regenerateSection(section)}
                      >
                        Regenerate
                      </Button>
                      <Button size="sm" variant="danger" leftIcon={<Trash2 className="w-3.5 h-3.5" />} onClick={() => deleteSection(section.section)}>
                        Delete
                      </Button>
                    </div>
                  </div>

                  {/* Questions */}
                  <ul className="divide-y divide-slate-100">
                    {section.questions?.map((q: any, idx: number) => {
                      const qKey = `${section.section}-${idx}`;
                      return (
                        <li key={idx} className="px-5 py-3 flex items-start gap-3">
                          <span className="text-xs font-bold text-slate-400 mt-0.5 w-5 shrink-0">Q{idx + 1}</span>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-slate-800">{q.text}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="info">{q.marks}m</Badge>
                              <Badge variant="default">{q.blooms_taxonomy_level}</Badge>
                              {q.topic && <span className="text-xs text-slate-400">{q.topic}</span>}
                            </div>
                          </div>
                          <Button
                            size="sm" variant="ghost"
                            loading={loadingQuestion === qKey}
                            leftIcon={<RefreshCw className="w-3 h-3" />}
                            onClick={() => regenerateQuestion(section, idx)}
                          >
                            Regen
                          </Button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {tab !== "edit" && (pdfUrl || docUrl) && (
          <div className="flex items-center gap-3 px-6 py-3 border-t border-slate-200 bg-white rounded-b-2xl">
            {pdfUrl && (
              <a href={pdfUrl} target="_blank" rel="noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-700 transition-colors"
              >
                <Download className="w-4 h-4" /> Download PDF
              </a>
            )}
            {docUrl && (
              <a href={docUrl} target="_blank" rel="noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Download className="w-4 h-4" /> Download DOCX
              </a>
            )}
          </div>
        )}
      </div>
    </div>
  );
}