import {
  Sparkles,
  FileText,
 Blocks,
  RefreshCcw,
  Download,
  ShieldCheck,
} from "lucide-react";

import Section from "@/components/ui/Section";
import Heading from "@/components/ui/Heading";

const features = [
  {
    icon: Sparkles,
    title: "AI Question Generation",
    description:
      "Generate balanced examination papers from your syllabus using retrieval-augmented AI.",
  },
  {
    icon: Blocks,
    title: "Fully Configurable",
    description:
      "Control marks, sections, Bloom's taxonomy, question types and overall paper structure.",
  },
  {
    icon: RefreshCcw,
    title: "Regenerate Instantly",
    description:
      "Replace individual questions without affecting the rest of the examination.",
  },
  {
    icon: FileText,
    title: "Professional Formatting",
    description:
      "Every paper is cleanly structured and ready for review before export.",
  },
  {
    icon: Download,
    title: "Export Anywhere",
    description:
      "Download directly as PDF or DOCX without additional formatting.",
  },
  {
    icon: ShieldCheck,
    title: "Private by Design",
    description:
      "Your uploaded material remains yours and is never used to train public models.",
  },
];

export default function Features() {
  return (
    <Section dividerBottom>

      <Heading
        eyebrow="Capabilities"
        title="Everything you need. Nothing you don't."
        description="Every feature is designed to reduce repetitive work while keeping educators in complete control."
        className="mb-24"
      />

      <div className="grid lg:grid-cols-2 gap-x-20">

        {features.map((feature, index) => {

          const Icon = feature.icon;

          return (
            <div
              key={feature.title}
              className={`
                flex
                gap-6
                py-10

                ${
                  index < features.length - 2
                    ? "border-b border-[var(--qc-divider)]"
                    : ""
                }
              `}
            >

              <div
                className="
                  w-11
                  h-11
                  rounded-full

                  flex
                  items-center
                  justify-center

                  bg-[var(--qc-primary-light)]

                  shrink-0
                "
              >
                <Icon
                  className="
                    w-5
                    h-5
                    text-[var(--qc-primary)]
                  "
                />
              </div>

              <div>

                <h3
                  className="
                    text-xl
                    font-semibold
                    tracking-[-0.02em]
                    text-[var(--qc-text)]
                    mb-3
                  "
                >
                  {feature.title}
                </h3>

                <p
                  className="
                    text-base
                    leading-8
                    text-[var(--qc-text-secondary)]
                  "
                >
                  {feature.description}
                </p>

              </div>

            </div>
          );

        })}

      </div>

    </Section>
  );
}