import { ArrowRight } from "lucide-react";

import Button from "@/components/ui/Button";
import Heading from "@/components/ui/Heading";
import Section from "@/components/ui/Section";

interface CTAProps {
  onGetStarted?: () => void;
}

export default function CTA({
  onGetStarted,
}: CTAProps) {
  return (
    <Section>

      <div className="max-w-4xl mx-auto text-center">

        <Heading
          align="center"
          size="lg"
          title={
            <>
              Create better assessments.
              <br />
              Starting today.
            </>
          }
          description="
            Join educators using QuestionCraft to transform hours
            of manual work into a streamlined, intelligent workflow.
          "
        />

        <div className="mt-14 flex justify-center">

          <Button
            size="lg"
            onClick={onGetStarted}
            rightIcon={<ArrowRight className="w-4 h-4" />}
          >
            Start Creating
          </Button>

        </div>

        <p
          className="
            mt-8
            text-sm
            text-[var(--qc-text-muted)]
          "
        >
          Free to get started.
          No credit card required.
        </p>

      </div>

    </Section>
  );
}