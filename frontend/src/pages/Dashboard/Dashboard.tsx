import HeroActions from "@/components/dashboard/HeroActions";
import RecentPapers from "@/components/dashboard/RecentPapers";
import ContinueWorking from "@/components/dashboard/ContinueWorking";
import TemplateSection from "@/components/dashboard/TemplateSection";

import CreditUsageCard from "@/components/dashboard/CreditUsageCard";
import AIInsightsCard from "@/components/dashboard/AIInsightsCard";
import ActivityCard from "@/components/dashboard/ActivityCard";

import { DashboardPage } from "@/components/dashboard/DashboardSidebar";

interface DashboardProps {
  onNavigate: (page: DashboardPage) => void;
}

export default function Dashboard({
  onNavigate,
}: DashboardProps) {
  return (
    <div className="grid grid-cols-12 gap-8">

      {/* LEFT */}

      <div className="col-span-8 space-y-8">

        <HeroActions
          userName="Rishikesh"
          onGenerate={() =>
            onNavigate("generate")
          }
          onTemplates={() => {}}
          onQuestionBanks={() =>
            onNavigate("question-bank")
          }
        />

        <RecentPapers
          papers={[]}
          onViewAll={() =>
            onNavigate("history")
          }
          onPreview={() => {}}
          onDuplicate={() => {}}
          onExport={() => {}}
        />

        <ContinueWorking
          drafts={[]}
          onResume={() => {}}
        />

        <TemplateSection
          templates={[
            {
              id: "1",
              name: "Mid Semester",
              description:
                "Standard university mid-sem examination format.",
            },
            {
              id: "2",
              name: "End Semester",
              description:
                "Comprehensive final examination template.",
            },
            {
              id: "3",
              name: "Quiz",
              description:
                "Short formative assessment template.",
            },
          ]}
          onSelect={() => {}}
        />

      </div>

      {/* RIGHT */}

      <div className="col-span-4 space-y-6">

        <CreditUsageCard
          planName="Professional"
          usedCredits={42}
          totalCredits={200}
        />

        <AIInsightsCard
          bloomCoverage={84}
          averageDifficulty="Medium"
          suggestions={[
            "Increase HOTS questions.",
            "Reduce Unit 2 repetition.",
            "Include one case-study question.",
          ]}
        />

        <ActivityCard
          activities={[
            {
              id: "1",
              type: "generate",
              title:
                "Generated Operating Systems Paper",
              time: "15 minutes ago",
            },
            {
              id: "2",
              type: "upload",
              title:
                "Uploaded DBMS Syllabus",
              time: "Yesterday",
            },
            {
              id: "3",
              type: "draft",
              title:
                "Saved Computer Networks Draft",
              time: "2 days ago",
            },
          ]}
        />

      </div>

    </div>
  );
}