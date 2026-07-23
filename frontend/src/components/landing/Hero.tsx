import { ArrowRight, Play, Check } from "lucide-react";

import Button from "@/components/ui/Button";
import Container from "@/components/ui/Container";
import Section from "@/components/ui/Section";

interface HeroProps {
  onGetStarted?: () => void;
}

export default function Hero({ onGetStarted }: HeroProps) {
  return (
    <Section className="pt-10 lg:pt-20 pb-28">

      <Container>

        <div className="max-w-4xl">

          {/* Hero Heading */}

<div className="mb-10">

  <div className="flex items-start gap-5">

    {/* <img
      src="/logo.png"
      alt="QuestionCraft"
      className="
w-26
h-26
shrink-0
relative
translate-y-[-28px]
"
    /> */}

    <h1
      className="
        text-5xl
        sm:text-6xl
        lg:text-7xl

        font-semibold

        tracking-[-0.06em]

        leading-[0.98]

        text-[var(--qc-text)]
      "
    >
      Every great examination
    </h1>

  </div>

  <h1
    className="
      text-5xl
      sm:text-6xl
      lg:text-7xl

      font-semibold

      tracking-[-0.06em]

      leading-[0.98]

      text-[var(--qc-text)]
      mt-1
    "
  >
    starts with
    <br />
    a better question.
  </h1>

</div>

          {/* Description */}

          <p
            className="
              mt-10

              max-w-2xl

              text-xl

              leading-9

              text-[var(--qc-text-secondary)]
            "
          >
            Generate professional examination papers from your syllabus
            in minutes. Configure your assessment, review every question,
            and export beautifully formatted papers with complete control.
          </p>

          {/* Buttons */}

          <div className="mt-14 flex flex-wrap items-center gap-4">

            <Button
              size="lg"
              onClick={onGetStarted}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Start Creating
            </Button>

            <Button
              size="lg"
              variant="secondary"
              leftIcon={<Play className="w-4 h-4 fill-current" />}
            >
              Watch Demo
            </Button>

          </div>

          {/* Trust Row */}

          <div
            className="
              mt-14

              flex

              flex-wrap

              gap-x-8

              gap-y-4

              text-sm

              text-[var(--qc-text-secondary)]
            "
          >

            {[
              "No credit card required",
              "PDF & DOCX export",
              "Edit every question",
              "Built for educators",
            ].map((item) => (

              <div
                key={item}
                className="flex items-center gap-2"
              >

                <Check
                  className="
                    w-4
                    h-4
                    text-[var(--qc-primary)]
                  "
                />

                {item}

              </div>

            ))}

          </div>

        </div>

      </Container>

    </Section>
  );
}