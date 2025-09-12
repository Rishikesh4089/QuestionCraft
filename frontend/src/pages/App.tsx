import { useState } from "react";
import FileUploadSection from "../components/FileUploadSection";
import PaperSettingsSection from "../components/PaperSettingsSection";
import DifficultySplitSection from "../components/DifficultySplitSection";
import UnitSplitSection from "../components/UnitSplitSection";
import QuestionPaperDisplay from "../components/QuestionPaperDisplay";
import InitialPlaceholder from "../components/InitialPlaceholder";
import LoadingPlaceholder from "../components/LoadingPlaceholder";
import { generateMockPaper } from "../utils/mockApi";
import type { Paper } from "../types/paper";

function App() {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(false);

  // ✅ Added missing state
  const [totalMarks, setTotalMarks] = useState<number>(100);

  const handleGenerate = async (settings: any) => {
    setLoading(true);
    setPaper(null);

    try {
      const generated = await generateMockPaper(settings);
      setPaper(generated);
    } catch (err) {
      console.error("Error generating paper:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4">
      <h1 className="text-3xl font-bold text-indigo-700 mb-6">
        📄 Question Paper Generator
      </h1>

      {/* File Upload */}
      <FileUploadSection onUpload={(file) => console.log("Uploaded:", file)} />

      {/* Settings Sections */}
      <PaperSettingsSection
        onGenerate={handleGenerate}
        totalMarks={totalMarks}
        onTotalMarksChange={setTotalMarks}
      />
      <DifficultySplitSection
        difficulty={0}
        onDifficultyChange={() => {}}
      />
      <UnitSplitSection
        units={[]}
        onUnitChange={() => {}}
        onAddUnit={() => {}}
        onRemoveUnit={() => {}}
      />

      {/* Display Section */}
      <div className="w-full max-w-4xl mt-10">
        {loading && <LoadingPlaceholder />}
        {!loading && !paper && <InitialPlaceholder />}
        {!loading && paper && <QuestionPaperDisplay paper={paper} />}
      </div>
    </div> // ✅ fixed closing div
  );
}

export default App;
