import Section from "@/components/ui/Section";
import Heading from "@/components/ui/Heading";

const benefits = [
  {
    title: "Designed for educators.",
    description:
      "Every workflow is built around how teachers, professors and institutions actually create assessments—not around AI for the sake of AI.",
  },
  {
    title: "Professional by default.",
    description:
      "Generate clean, structured examination papers that require little to no manual formatting before distribution.",
  },
  {
    title: "Remain in complete control.",
    description:
      "Review, edit and regenerate individual questions while keeping the overall structure intact.",
  },
  {
    title: "Save hours every semester.",
    description:
      "Reduce repetitive work and spend more time teaching instead of formatting documents.",
  },
  {
    title: "Built to scale.",
    description:
      "Whether you're creating one quiz or hundreds of examinations across departments, the workflow stays consistent.",
  },
  {
    title: "A foundation for modern assessment.",
    description:
      "QuestionCraft grows with your institution—from individual educators today to collaborative assessment management tomorrow.",
  },
];

export default function WhyQuestionCraft() {
  return (
    <Section dividerBottom>

      <Heading
        eyebrow="Why QuestionCraft"
        title="Designed for the way educators actually work."
        description="Every decision inside QuestionCraft is made to remove repetitive work while preserving academic quality."
        className="mb-24"
      />

      <div className="grid lg:grid-cols-2 border-t border-[var(--qc-divider)]">

        {benefits.map((benefit, index) => (

          <div
            key={benefit.title}
            className={`
              py-12
              pr-12

              ${
                index % 2 === 0
                  ? "lg:border-r border-[var(--qc-divider)]"
                  : ""
              }

              ${
                index < 4
                  ? "border-b border-[var(--qc-divider)]"
                  : ""
              }
            `}
          >

            <h3
              className="
                text-2xl
                font-semibold
                tracking-[-0.03em]
                text-[var(--qc-text)]
                mb-5
              "
            >
              {benefit.title}
            </h3>

            <p
              className="
                text-lg
                leading-8
                text-[var(--qc-text-secondary)]
              "
            >
              {benefit.description}
            </p>

          </div>

        ))}

      </div>

    </Section>
  );
}