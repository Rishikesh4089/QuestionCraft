import Section from "@/components/ui/Section";
import Heading from "@/components/ui/Heading";

const steps = [
  {
    number: "01",
    title: "Upload your material",
    description:
      "Import PDFs, lecture notes, presentations, or previous examinations.",
  },
  {
    number: "02",
    title: "Configure your paper",
    description:
      "Define marks, sections, Bloom levels, question types and difficulty.",
  },
  {
    number: "03",
    title: "Generate instantly",
    description:
      "QuestionCraft creates balanced, curriculum-aligned assessments in minutes.",
  },
  {
    number: "04",
    title: "Review & export",
    description:
      "Edit individual questions and export directly to PDF or DOCX.",
  },
];

export default function Workflow() {
  return (
    <Section dividerTop dividerBottom id="workflow">
      <Heading
        eyebrow="How it works"
        title="From syllabus to examination in four simple steps."
        description="A workflow designed to feel effortless while giving you complete control."
        className="mb-24"
      />

      <div className="divide-y divide-[var(--qc-divider)]">
        {steps.map((step) => (
          <div
            key={step.number}
            className="
              grid
              grid-cols-12
              gap-8
              py-12
              items-start
            "
          >
            <div className="col-span-2">
              <p
                className="
                  text-5xl
                  font-semibold
                  tracking-[-0.05em]
                  text-[var(--qc-primary)]
                "
              >
                {step.number}
              </p>
            </div>

            <div className="col-span-10 lg:col-span-4">
              <h3
                className="
                  text-2xl
                  font-semibold
                  tracking-[-0.03em]
                  text-[var(--qc-text)]
                "
              >
                {step.title}
              </h3>
            </div>

            <div className="col-span-12 lg:col-span-6">
              <p
                className="
                  text-lg
                  leading-8
                  text-[var(--qc-text-secondary)]
                "
              >
                {step.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}