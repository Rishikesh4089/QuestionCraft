import { useState } from "react";
import { Upload, Sparkles, X, Download } from "lucide-react";
import { supabase } from "../lib/supabase";
import { useAuth } from "../contexts/AuthContext";
import { generatePaperPDF, generatePaperDOCX } from "../utils/fileGenerators";
import CoolBlobEffect from "@/components/ui/cool-blob-effect";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function GeneratePaper() {
  const { user } = useAuth();

  // ----- State -----
  const [step, setStep] = useState<"upload" | "configure" | "generate">("upload");
  const [files, setFiles] = useState<File[]>([]);
  const [organization, setOrganization] = useState("");
  const [program, setProgram] = useState("");
  const [course, setCourse] = useState("");
  const [examName, setExamName] = useState("");
  const [examDate, setExamDate] = useState("");
  const [subject, setSubject] = useState("");
  const [totalMarks, setTotalMarks] = useState(100);
  const [questionTypes, setQuestionTypes] = useState([
    { id: "1", type: "Short Answer", marks: 4, count: 5, total: 20 },
    { id: "2", type: "Long Answer", marks: 10, count: 8, total: 80 },
  ]);
  const [generating, setGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [pdfUrl, setPdfUrl] = useState("");
  const [docUrl, setDocUrl] = useState("");
  const [generatedPaper, setGeneratedPaper] = useState<any>(null);

  // ----- File handling -----
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const uploadedFiles = Array.from(e.target.files || []);
    setFiles((prev) => [...prev, ...uploadedFiles]);
  };

  const removeFile = (fileName: string) =>
    setFiles((prev) => prev.filter((f) => f.name !== fileName));

  // ----- Question types -----
  // const QUESTION_TYPE_OPTIONS = [
  //   "Very Short Answer",
  //   "Short Answer",
  //   "Long Answer",
  //   "Essay",
  //   "Multiple Choice",
  // ];

  const addQuestionType = () =>
    setQuestionTypes((prev) => [
      ...prev,
      { id: Date.now().toString(), type: "Short Answer", marks: 2, count: 1, total: 2 },
    ]);

  const updateQuestionType = (id: string, field: string, value: string | number) => {
    setQuestionTypes((prev) =>
      prev.map((qt) =>
        qt.id === id
          ? {
              ...qt,
              [field]: value,
              total:
                field === "marks" || field === "count"
                  ? Number(field === "marks" ? value : qt.marks) *
                    Number(field === "count" ? value : qt.count)
                  : qt.total,
            }
          : qt
      )
    );
  };

  const removeQuestionType = (id: string) =>
    setQuestionTypes((prev) => prev.filter((qt) => qt.id !== id));

  // ----- Upload helper -----
  const uploadToSupabase = async (fileName: string, fileBlob: Blob, _type: string) => {
    if (!user?.id) throw new Error("User not logged in");
    const filePath = `${user.id}/${Date.now()}_${fileName}`;

    const { error } = await supabase.storage
      .from("papers")
      .upload(filePath, fileBlob, { upsert: true });
    if (error) throw error;

    const { data, error: urlError } = await supabase.storage
      .from("papers")
      .createSignedUrl(filePath, 3600);
    if (urlError) throw urlError;

    return data.signedUrl;
  };

  // ----- Generate Paper -----
// ----- Generate Paper -----
const handleGenerate = async () => {
  if (!subject || files.length === 0) {
    alert("Please upload syllabus files and specify subject.");
    return;
  }

  setGenerating(true);
  try {
    const formData = new FormData();
    formData.append("subject", subject);
    formData.append("difficulty_level", "Medium");
    formData.append("organization", organization);
    formData.append("program", program);
    formData.append("course", course);
    formData.append("exam_date", examDate);
    formData.append("exam_name", examName);

    files.forEach((file) => formData.append("syllabus_files", file));

    const patternJSON = {
      total_marks: totalMarks,
      instructions: [
        "Answer all questions in Section A and any two in Section B.",
        "Figures to the right indicate marks.",
      ],
      question_structure: questionTypes.map((qt, index) => ({
        section: String.fromCharCode(65 + index),
        question_type: qt.type,
        marks_each: qt.marks,
        question_count: qt.count,
      })),
    };

    formData.append("manual_pattern_json", JSON.stringify(patternJSON));

    const response = await fetch(`${API_BASE_URL}/generate-paper/`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Failed to generate paper via backend");
    const result = await response.json();
    setGeneratedPaper(result);

    // Generate files locally
    const pdfBlob = await generatePaperPDF(result);
    const docBlob = await generatePaperDOCX(result);

    const pdfLink = await uploadToSupabase("question_paper.pdf", pdfBlob, "application/pdf");
    const docLink = await uploadToSupabase(
      "question_paper.docx",
      docBlob,
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    );

    setPdfUrl(pdfLink);
    setDocUrl(docLink);

    // ✅ Save to `previous_papers` as Draft
    const { error } = await supabase.from("previous_papers").insert([
      {
        user_id: user?.id,
        paper_title: `${subject} - ${examName || "Exam"}`,
        subject_name: subject,
        total_marks: totalMarks,
        status: "Draft", // ✅ default
        paper_structure: result, // ✅ store full JSON
        pdf_url: pdfLink,
        docx_url: docLink,
      },
    ]);

    if (error) throw error;

    setShowPreview(true);
  } catch (error: any) {
    console.error("❌ Generation failed:", error.message);
    alert(error.message || "Failed to generate paper");
  } finally {
    setGenerating(false);
  }
};

  const totalCalculated = questionTypes.reduce((sum, qt) => sum + qt.total, 0);

  return (
    <div className="relative flex-1 overflow-auto bg-slate-50 min-h-screen">
      {/* 🌀 Animated Cool Blob Background */}
      <div className="absolute inset-0 z-0 opacity-60 pointer-events-none">
        <CoolBlobEffect />
      </div>
      <div className="max-w-6xl mx-auto p-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Generate Question Paper
        </h1>
        <p className="text-slate-600 mb-8">
          Upload materials and configure your paper pattern
        </p>

        {step === "upload" && (
          <UploadStep
            files={files}
            handleFileUpload={handleFileUpload}
            removeFile={removeFile}
            next={() => setStep("configure")}
          />
        )}
        {step === "configure" && (
          <ConfigureStep
            totalMarks={totalMarks}
            setTotalMarks={setTotalMarks}
            questionTypes={questionTypes}
            updateQuestionType={updateQuestionType}
            addQuestionType={addQuestionType}
            removeQuestionType={removeQuestionType}
            totalCalculated={totalCalculated}
            organization={organization}
            setOrganization={setOrganization}
            program={program}
            setProgram={setProgram}
            course={course}
            setCourse={setCourse}
            examName={examName}
            setExamName={setExamName}
            examDate={examDate}
            setExamDate={setExamDate}
            subject={subject}
            setSubject={setSubject}
            next={() => setStep("generate")}
            back={() => setStep("upload")}

          />
        )}
        {step === "generate" && (
          <GenerateStep
            generating={generating}
            handleGenerate={handleGenerate}
            back={() => setStep("configure")}
            prev={() => setStep("configure")}
          />
        )}
      </div>

      {showPreview && generatedPaper && (
        <PreviewModal
          pdfUrl={pdfUrl}
          docUrl={docUrl}
          generatedPaper={generatedPaper}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
}

/* -------------------- HELPER COMPONENTS -------------------- */

function UploadStep({ files, handleFileUpload, removeFile, next }: any) {
  return (
    <div className="bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-white/20">
      <h2 className="text-xl font-semibold mb-4">Upload Study Materials</h2>
      <div className="border-2 border-dashed p-12 text-center rounded-lg">
        <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <input
          type="file"
          multiple
          accept=".pdf,.pptx,.txt"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="cursor-pointer bg-slate-800 text-white px-4 py-2 rounded-lg hover:bg-slate-700"
        >
          Choose Files
        </label>
      </div>

      {files.length > 0 && (
        <>
          <div className="mt-6 space-y-2">
            {files.map((f: File, index: number) => (
              <div
                key={f.name || index}
                className="flex justify-between bg-slate-50 p-2 rounded-lg"
              >
                <span>{f.name}</span>
                <button
                  onClick={() => removeFile(f.name)}
                  className="text-red-500 hover:underline"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={next}
            className="mt-6 w-full bg-slate-800 text-white py-3 rounded-lg hover:bg-slate-700"
          >
            Continue to Configuration
          </button>
        </>
      )}
    </div>
  );
}


function ConfigureStep({
  totalMarks,
  setTotalMarks,
  questionTypes,
  updateQuestionType,
  addQuestionType,
  removeQuestionType,
  totalCalculated,
  organization,
  setOrganization,
  program,
  setProgram,
  course,
  setCourse,
  examName,
  setExamName,
  examDate,
  setExamDate,
  subject,
  setSubject,
  next,
  back, // ✅ FIX: destructure back here
}: any) {
  const QUESTION_TYPE_OPTIONS = [
    "Very Short Answer",
    "Short Answer",
    "Long Answer",
    "Essay",
    "Multiple Choice",
  ];

  return (
    <div className="space-y-6">
      {/* ✅ Card container made opaque with blur */}
      <div className="bg-white/95 backdrop-blur-sm rounded-xl p-8 shadow-lg border border-white/20">
        <h2 className="text-xl font-semibold mb-6">Paper Configuration</h2>

        {/* Header Fields */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <input
            placeholder="Organization Name"
            value={organization}
            onChange={(e) => setOrganization(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            placeholder="Program Name"
            value={program}
            onChange={(e) => setProgram(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            placeholder="Course Name"
            value={course}
            onChange={(e) => setCourse(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            placeholder="Exam Name (e.g. Midterm)"
            value={examName}
            onChange={(e) => setExamName(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            type="date"
            value={examDate}
            onChange={(e) => setExamDate(e.target.value)}
            className="border p-2 rounded"
          />
          <input
            placeholder="Subject Name"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            className="border p-2 rounded"
          />
        </div>

        <div className="flex justify-between mb-4">
          <label>Total Marks:</label>
          <input
            type="number"
            value={totalMarks}
            onChange={(e) => setTotalMarks(Number(e.target.value))}
            className="border p-1 rounded w-24"
          />
        </div>

        {/* Question Type Config */}
        <div className="mb-2 font-medium">Question Types:</div>
        {questionTypes.map((qt: any, _index: number) => (
          <div key={qt.id} className="flex items-center gap-3 mb-3">
            <select
              value={qt.type}
              onChange={(e) => updateQuestionType(qt.id, "type", e.target.value)}
              className="border p-1 rounded flex-1"
            >
              {QUESTION_TYPE_OPTIONS.map((opt) => (
                <option key={opt}>{opt}</option>
              ))}
            </select>
            <div className="flex flex-col items-center">
              <label className="text-xs text-slate-500">Marks Each</label>
              <input
                type="number"
                value={qt.marks}
                onChange={(e) =>
                  updateQuestionType(qt.id, "marks", Number(e.target.value))
                }
                className="border p-1 rounded w-20"
              />
            </div>
            <div className="flex flex-col items-center">
              <label className="text-xs text-slate-500">Questions</label>
              <input
                type="number"
                value={qt.count}
                onChange={(e) =>
                  updateQuestionType(qt.id, "count", Number(e.target.value))
                }
                className="border p-1 rounded w-20"
              />
            </div>
            <button
              onClick={() => removeQuestionType(qt.id)}
              className="text-red-500 hover:underline"
            >
              ✕
            </button>
          </div>
        ))}

        <button onClick={addQuestionType} className="text-slate-800 hover:underline">
          + Add Question Type
        </button>

        <div className="text-right mt-4 font-medium">
          Total: {totalCalculated} / {totalMarks}
        </div>
      </div>

      {/* ✅ Navigation Buttons */}
      <div className="flex justify-between mt-6">
        <button
          onClick={back}
          className="px-6 py-3 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300 transition-colors"
        >
          ← Back
        </button>
        <button
          onClick={next}
          className="px-6 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors"
        >
          Review & Generate →
        </button>
      </div>
    </div>
  );
}


function GenerateStep({ generating, handleGenerate, prev }: any) {
  return (
    <div className="space-y-4">
      {/* ✅ Opaque, glass-like container */}
      <div className="bg-white/95 backdrop-blur-sm p-8 rounded-xl shadow-lg border border-white/20">
        <h2 className="text-xl font-semibold mb-4">Ready to Generate?</h2>
        <p className="text-slate-600 mb-6">
          The system will analyze your syllabus and generate a question paper
          following the specified pattern.
        </p>

        <div className="flex space-x-4">
          {/* 🔙 Back button */}
          <button
            onClick={prev}
            className="flex-1 py-3 bg-slate-200 text-slate-800 rounded-lg hover:bg-slate-300 transition-colors"
          >
            ← Back
          </button>

          {/* ⚙️ Generate button */}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="flex-1 py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 flex items-center justify-center space-x-2 disabled:opacity-50 transition-all"
          >
            {generating ? (
              <Sparkles className="w-5 h-5 animate-spin" />
            ) : (
              <Sparkles className="w-5 h-5" />
            )}
            <span>{generating ? "Generating..." : "Generate Paper"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}


function PreviewModal({ pdfUrl, docUrl, generatedPaper, onClose }: any) {
  const [tab, setTab] = useState<"pdf" | "json" | "edit">("pdf");
  const [editablePaper, setEditablePaper] = useState<any>(generatedPaper);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);

  // ============================================================
  // 🧠 Delete Section
  // ============================================================
  const deleteSection = (sectionName: string) => {
    setEditablePaper((prev: any) => ({
      ...prev,
      sections: prev.sections.filter((s: any) => s.section !== sectionName),
    }));
  };

  // ============================================================
  // 🔁 Regenerate Entire Section
  // ============================================================
  const regenerateSection = async (section: any) => {
    try {
      const response = await fetch(`${API_BASE_URL}/regenerate-section/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(section), // ✅ send section directly
      });

      if (!response.ok) throw new Error("Failed to regenerate section");
      const data = await response.json();

      // ✅ Normalize response (sometimes backend wraps it in {section: {...}})
      const newSection = data.section ? data.section : data;

      // ✅ Update state safely
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
        status: "Final",
        paper_structure: editablePaper, // ✅ save the edited version
        updated_at: new Date().toISOString(),
        last_edited: new Date().toISOString(),
      })
      .eq("subject_name", editablePaper.subject_name || editablePaper.subject);

    if (error) throw error;

    alert("✅ Paper finalized successfully!");
    setEditing(false);
    setSaving(false);
    setTab("pdf");
  } catch (err: any) {
    console.error(err);
    alert("❌ Failed to finalize paper: " + err.message);
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
          <h3 className="text-lg font-semibold">Generated Question Paper</h3>
          <div className="flex space-x-3 items-center">
            {!editing ? (
              <button
                onClick={() => setEditing(true)}
                className="px-3 py-1.5 text-sm bg-yellow-500 text-white rounded-lg hover:bg-yellow-400 transition-all"
              >
                Edit Paper
              </button>
            ) : (
              <button
                onClick={saveFinalPaper}
                disabled={saving}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-500 disabled:opacity-50 transition-all"
              >
                {saving ? "Saving..." : "✅ Save Final Paper"}
              </button>
            )}
            <button onClick={onClose} className="text-slate-500 hover:text-slate-800">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b text-sm font-medium">
          {!editing ? (
            <>
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
            </>
          ) : (
            <button className="flex-1 py-2 bg-slate-200 font-semibold">Edit Mode</button>
          )}
        </div>

        {/* Body */}
        <div className="flex-1 overflow-auto bg-slate-50 p-6">
          {!editing ? (
            tab === "pdf" ? (
              pdfUrl ? (
                <iframe
                  src={pdfUrl}
                  className="w-full h-full rounded-lg border"
                  title="Question Paper PDF Preview"
                />
              ) : (
                <p className="text-center text-slate-500 mt-20">PDF not available.</p>
              )
            ) : (
              <pre className="text-sm text-slate-800 bg-white rounded-lg p-4 border overflow-auto h-full">
                {JSON.stringify(editablePaper, null, 2)}
              </pre>
            )
          ) : (
            <div className="space-y-6">
              {editablePaper.sections.map((section: any) => (
                <div key={section.section} className="bg-white border rounded-lg shadow-sm p-4">
                  <div className="flex justify-between items-center border-b pb-2 mb-3">
                    <h4 className="font-semibold text-slate-800">
                      Section {section.section} - {section.question_type}
                    </h4>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => regenerateSection(section)}
                        className="text-blue-600 text-sm font-medium transition-all duration-200 transform hover:scale-110 hover:font-semibold"
                      >
                        Regenerate Section
                      </button>
                      <button
                        onClick={() => deleteSection(section.section)}
                        className="text-red-500 text-sm font-medium transition-all duration-200 transform hover:scale-110 hover:font-semibold"
                      >
                        🗑 Delete
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
                          className="text-blue-600 text-xs transition-all duration-200 transform hover:scale-125 hover:font-semibold"
                        >
                          Regenerate
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        {!editing && (
          <div className="flex justify-between items-center p-4 border-t bg-slate-100">
            <a
              href={pdfUrl}
              target="_blank"
              className="flex items-center bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-500 transition-all"
            >
              <Download className="w-4 h-4 mr-2" /> Download PDF
            </a>
            <a
              href={docUrl}
              target="_blank"
              className="flex items-center bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-500 transition-all"
            >
              <Download className="w-4 h-4 mr-2" /> Download DOCX
            </a>
          </div>
        )}
      </div>
    </div>
  );
}