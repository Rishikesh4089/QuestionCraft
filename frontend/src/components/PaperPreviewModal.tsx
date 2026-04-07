import { useState } from "react";
import { X, Download } from "lucide-react";
import { supabase } from "../lib/supabase";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface PaperPreviewModalProps {
  pdfUrl?: string;
  docUrl?: string;
  initialPaper: any;
  mode?: "view" | "edit";
  onClose: () => void;
}

export default function PaperPreviewModal({
  pdfUrl,
  docUrl,
  initialPaper,
  mode = "view",
  onClose,
}: PaperPreviewModalProps) {
  const [editablePaper, setEditablePaper] = useState(initialPaper);
  const [saving, setSaving] = useState(false);

  const [editing, setEditing] = useState(mode === "edit");
  const [tab, setTab] = useState<"pdf" | "json" | "edit">("pdf");

  // ============================================================
  // 🔁 Regenerate Entire Section
  // ============================================================
  const regenerateSection = async (section: any) => {
    try {
      const response = await fetch(`${API_BASE_URL}/regenerate-section/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(section),
      });

      if (!response.ok) throw new Error("Failed to regenerate section");
      const data = await response.json();
      const newSection = data.section ? data.section : data;

      setEditablePaper((prev: any) => ({
        ...prev,
        sections: prev.sections.map((s: any) =>
          s.section === section.section ? newSection : s
        ),
      }));
    } catch (err) {
      console.error(err);
      alert("❌ Failed to regenerate section");
    }
  };

  // ============================================================
  // 🔁 Regenerate Single Question
  // ============================================================
  const regenerateQuestion = async (section: any, questionIndex: number) => {
    const sectionName = section.section;
    const targetQuestion = section.questions[questionIndex];
    const prevQuestions = section.questions.map((q: any) => q.text);

    try {
      const response = await fetch(`${API_BASE_URL}/regenerate-question/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          subject: editablePaper.subject,
          section: sectionName,
          question_type: section.question_type,
          topic: targetQuestion.topic || "General Topic",
          difficulty_level: "Medium",
          previous_questions: prevQuestions,
        }),
      });

      const data = await response.json();

      if (data.success && data.new_question) {
        const newQ = data.new_question;
        setEditablePaper((prev: any) => ({
          ...prev,
          sections: prev.sections.map((s: any) =>
            s.section === sectionName
              ? {
                  ...s,
                  questions: s.questions.map((q: any, i: number) =>
                    i === questionIndex ? newQ : q
                  ),
                }
              : s
          ),
        }));
      } else {
        alert("⚠️ Could not regenerate question.");
      }
    } catch (err) {
      console.error(err);
      alert("❌ Regeneration failed.");
    }
  };

  // ============================================================
  // 💾 Save Final Paper
  // ============================================================
  const saveFinalPaper = async () => {
    setSaving(true);
    try {
      const { error } = await supabase
        .from("previous_papers")
        .update({
          paper_structure: editablePaper,
          status: "Final",
          updated_at: new Date().toISOString(),
        })
        .eq("subject_name", editablePaper.subject_name || editablePaper.subject);

      if (error) throw error;

      alert("✅ Paper finalized successfully!");
      setEditing(false);
      setSaving(false);
      setTab("pdf");
    } catch (err: any) {
      console.error(err);
      alert("❌ Failed to save paper: " + err.message);
      setSaving(false);
    }
  };

  // ============================================================
  // 🧱 Render
  // ============================================================
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl w-11/12 max-w-6xl h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-3 border-b bg-slate-100">
          <h3 className="text-lg font-semibold">Question Paper Preview</h3>
          <div className="flex space-x-3 items-center">
            {editing ? (
              <button
                onClick={saveFinalPaper}
                disabled={saving}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-50"
              >
                {saving ? "Saving..." : "✅ Save Changes"}
              </button>
            ) : (
              <button
                onClick={() => setEditing(true)}
                className="px-3 py-1.5 text-sm bg-yellow-500 text-white rounded-lg hover:bg-yellow-400"
              >
                ✏️ Edit
              </button>
            )}
            <button onClick={onClose} className="text-slate-500 hover:text-slate-800">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        {!editing && (
          <div className="flex border-b text-sm font-medium">
            <button
              className={`flex-1 py-2 ${
                tab === "pdf" ? "bg-slate-200 font-semibold" : "hover:bg-slate-50"
              }`}
              onClick={() => setTab("pdf")}
            >
              PDF Preview
            </button>
            <button
              className={`flex-1 py-2 ${
                tab === "json" ? "bg-slate-200 font-semibold" : "hover:bg-slate-50"
              }`}
              onClick={() => setTab("json")}
            >
              JSON Structure
            </button>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-auto bg-slate-50 p-6">
          {editing ? (
            <div className="space-y-6">
              {editablePaper.sections.map((section: any) => (
                <div
                  key={section.section}
                  className="bg-white border rounded-lg shadow-sm p-4"
                >
                  <div className="flex justify-between items-center border-b pb-2 mb-3">
                    <h4 className="font-semibold text-slate-800">
                      Section {section.section} - {section.question_type}
                    </h4>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => regenerateSection(section)}
                        className="text-blue-600 text-sm hover:underline"
                      >
                        Regenerate Section
                      </button>
                    </div>
                  </div>
                  <ul className="space-y-2 text-slate-700">
                    {section.questions.map((q: any, idx: number) => (
                      <li
                        key={idx}
                        className="flex justify-between items-center text-sm border-b pb-1"
                      >
                        <div>
                          {idx + 1}. {q.text} ({q.marks} marks)
                          <p className="text-xs text-slate-500 italic">
                            [{q.blooms_taxonomy_level}] Topic: {q.topic}
                          </p>
                        </div>
                        <button
                          onClick={() => regenerateQuestion(section, idx)}
                          className="text-blue-600 text-xs hover:underline"
                        >
                          Regenerate
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          ) : tab === "pdf" ? (
            pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-full rounded-lg border"
                title="PDF Preview"
              />
            ) : (
              <p className="text-center text-slate-500 mt-20">
                No PDF available.
              </p>
            )
          ) : (
            <pre className="text-sm text-slate-800 bg-white rounded-lg p-4 border overflow-auto h-full">
              {JSON.stringify(editablePaper, null, 2)}
            </pre>
          )}
        </div>

        {/* Footer */}
        {!editing && (
          <div className="flex justify-between items-center p-4 border-t bg-slate-100">
            <a
              href={pdfUrl}
              target="_blank"
              className="flex items-center bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-500"
            >
              <Download className="w-4 h-4 mr-2" /> Download PDF
            </a>
            <a
              href={docUrl}
              target="_blank"
              className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-500"
            >
              <Download className="w-4 h-4 mr-2" /> Download DOCX
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
