import {
  ChevronDown,
} from "lucide-react";

import {
  useState,
} from "react";

import Section from "@/components/ui/Section";
import Heading from "@/components/ui/Heading";

const faqs = [
  {
    question: "Can I edit questions after they're generated?",
    answer:
      "Yes. Every generated question can be individually edited, replaced or regenerated before exporting.",
  },
  {
    question: "What file types can I upload?",
    answer:
      "QuestionCraft supports PDF documents initially, with DOCX and additional formats planned.",
  },
  {
    question: "Will my uploaded material be used to train AI models?",
    answer:
      "No. Your content remains private and is never used to train public AI models.",
  },
  {
    question: "Can I create multiple versions of the same paper?",
    answer:
      "Absolutely. You can regenerate individual questions or entire sections while keeping the same structure.",
  },
  {
    question: "Do you support Bloom's Taxonomy?",
    answer:
      "Yes. You can configure cognitive levels to create balanced assessments aligned with Bloom's Taxonomy.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState(0);

  return (
    <Section dividerBottom>

      <Heading
        eyebrow="FAQ"
        title="Questions, answered."
        description="Everything you need to know before getting started."
        align="center"
        className="mb-24"
      />

      <div className="max-w-4xl mx-auto">

        {faqs.map((faq, index) => {

          const expanded = open === index;

          return (

            <button
              key={faq.question}
              onClick={() =>
                setOpen(expanded ? -1 : index)
              }
              className="
                w-full
                text-left
                border-b
                border-[var(--qc-divider)]
                py-8
                transition-colors
                hover:bg-black/[0.015]
              "
            >

              <div className="flex justify-between items-start gap-8">

                <div>

                  <h3
                    className="
                      text-xl
                      font-medium
                      tracking-[-0.02em]
                      text-[var(--qc-text)]
                    "
                  >
                    {faq.question}
                  </h3>

                  {expanded && (

                    <p
                      className="
                        mt-5
                        text-lg
                        leading-8
                        text-[var(--qc-text-secondary)]
                        max-w-3xl
                      "
                    >
                      {faq.answer}
                    </p>

                  )}

                </div>

                <ChevronDown
                  className={`
                    w-5
                    h-5
                    shrink-0
                    transition-transform
                    duration-300
                    ${
                      expanded
                        ? "rotate-180"
                        : ""
                    }
                  `}
                />

              </div>

            </button>

          );

        })}

      </div>

    </Section>
  );
}