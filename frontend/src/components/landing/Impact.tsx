import Section from "@/components/ui/Section";
import Heading from "@/components/ui/Heading";

const stats = [
  {
    value: "80%",
    label: "Less time spent creating assessments",
  },
  {
    value: "<3 min",
    label: "Average paper generation time",
  },
  {
    value: "100%",
    label: "Editable before export",
  },
];

export default function Impact() {
  return (
    <Section dividerBottom>

      <Heading
        eyebrow="The Impact"
        title="Spend less time formatting. More time teaching."
        description="QuestionCraft removes repetitive work without taking control away from educators."
        align="center"
        maxWidth="md"
        className="mb-24"
      />

      <div className="grid md:grid-cols-3 border-t border-[var(--qc-divider)]">

        {stats.map((stat, index) => (

          <div
            key={stat.label}
            className={`
              py-16
              text-center

              ${
                index !== stats.length - 1
                  ? "md:border-r border-[var(--qc-divider)]"
                  : ""
              }
            `}
          >

            <h3
              className="
                text-6xl
                lg:text-7xl
                font-semibold
                tracking-[-0.05em]
                text-[var(--qc-primary)]
              "
            >
              {stat.value}
            </h3>

            <p
              className="
                mt-6
                text-lg
                leading-8
                text-[var(--qc-text-secondary)]
              "
            >
              {stat.label}
            </p>

          </div>

        ))}

      </div>

    </Section>
  );
}