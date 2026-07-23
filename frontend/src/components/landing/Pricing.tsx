import {
    Check,
    ArrowRight,
} from "lucide-react";

import Button from "@/components/ui/Button";
import Heading from "@/components/ui/Heading";
import Section from "@/components/ui/Section";

const plans = [
    {
        name: "Free",
        price: "₹0",
        subtitle: "Perfect for getting started.",
        button: "Start Free",
        primary: false,

        features: [
            "Limited AI generations",
            "PDF upload",
            "Question editing",
            "PDF export",
        ],
    },

    {
        name: "Pro",
        price: "Coming Soon",
        subtitle: "For educators creating assessments regularly.",
        button: "Join Waitlist",
        primary: true,

        features: [
            "Unlimited paper generation",
            "Advanced Bloom controls",
            "Question Bank",
            "Version History",
            "Priority AI generation",
            "DOCX + PDF export",
        ],
    },

    {
        name: "Enterprise",
        price: "Custom",
        subtitle: "Built for schools and universities.",
        button: "Contact Us",
        primary: false,

        features: [
            "Department management",
            "Faculty collaboration",
            "Central repository",
            "Institution dashboard",
            "Dedicated support",
        ],
    },
];

export default function Pricing() {
    return (
        <Section dividerBottom>

            <Heading
                eyebrow="Pricing"
                title="Simple pricing that grows with you."
                description="Start free. Upgrade when QuestionCraft becomes part of your everyday workflow."
                align="center"
                className="mb-24"
            />

            <div className="grid lg:grid-cols-3 gap-8">

                {plans.map((plan) => (

                    <div
                        key={plan.name}
                        className={`
                            rounded-[24px]

                            border

                            ${
                                plan.primary
                                    ? "border-[var(--qc-primary)] bg-white"
                                    : "border-[var(--qc-divider)] bg-[var(--qc-surface)]"
                            }

                            p-10

                            flex
                            flex-col
                        `}
                    >

                        <p
                            className="
                                text-sm
                                uppercase
                                tracking-[0.15em]
                                text-[var(--qc-primary)]
                                font-medium
                            "
                        >
                            {plan.name}
                        </p>

                        <h3
                            className="
                                mt-6
                                text-5xl
                                font-semibold
                                tracking-[-0.05em]
                                text-[var(--qc-text)]
                            "
                        >
                            {plan.price}
                        </h3>

                        <p
                            className="
                                mt-4
                                text-base
                                leading-7
                                text-[var(--qc-text-secondary)]
                            "
                        >
                            {plan.subtitle}
                        </p>

                        <Button
                            className="mt-10 w-full"
                            variant={
                                plan.primary
                                    ? "primary"
                                    : "secondary"
                            }
                            rightIcon={<ArrowRight className="w-4 h-4" />}
                        >
                            {plan.button}
                        </Button>

                        <div className="mt-10 border-t border-[var(--qc-divider)] pt-8 space-y-5">

                            {plan.features.map((feature) => (

                                <div
                                    key={feature}
                                    className="flex items-start gap-3"
                                >

                                    <Check
                                        className="
                                            w-5
                                            h-5
                                            text-[var(--qc-primary)]
                                            shrink-0
                                            mt-0.5
                                        "
                                    />

                                    <p
                                        className="
                                            text-[15px]
                                            leading-7
                                            text-[var(--qc-text-secondary)]
                                        "
                                    >
                                        {feature}
                                    </p>

                                </div>

                            ))}

                        </div>

                    </div>

                ))}

            </div>

        </Section>
    );
}