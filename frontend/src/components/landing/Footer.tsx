import Container from "@/components/ui/Container";

export default function Footer() {
  return (
    <footer className="border-t border-[var(--qc-divider)]">

      <Container>

        <div className="py-20">

          <div className="grid lg:grid-cols-4 gap-16">

            {/* Brand */}

            <div>

              <div className="flex items-center gap-3">

                <img
                  src="/logo.png"
                  alt="QuestionCraft"
                  className="w-8 h-8"
                />

                <span
                  className="
                    text-xl
                    font-medium
                    tracking-[-0.03em]
                    text-[var(--qc-text)]
                  "
                >
                  QuestionCraft
                </span>

              </div>

              <p
                className="
                  mt-6
                  text-[15px]
                  leading-7
                  text-[var(--qc-text-secondary)]
                  max-w-xs
                "
              >
                AI-powered assessment creation for educators,
                tutors and institutions.
              </p>

            </div>

            {/* Product */}

            <div>

              <h4
                className="
                  text-sm
                  uppercase
                  tracking-[0.15em]
                  font-medium
                  text-[var(--qc-text)]
                  mb-6
                "
              >
                Product
              </h4>

              <div className="space-y-4">

                <a
                  href="#features"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  Features
                </a>

                <a
                  href="#pricing"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  Pricing
                </a>

                <a
                  href="#faq"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  FAQ
                </a>

              </div>

            </div>

            {/* Company */}

            <div>

              <h4
                className="
                  text-sm
                  uppercase
                  tracking-[0.15em]
                  font-medium
                  text-[var(--qc-text)]
                  mb-6
                "
              >
                Company
              </h4>

              <div className="space-y-4">

                <a
                  href="/about"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  About
                </a>

                <a
                  href="/privacy"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  Privacy
                </a>

                <a
                  href="/terms"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  Terms
                </a>

              </div>

            </div>

            {/* Contact */}

            <div>

              <h4
                className="
                  text-sm
                  uppercase
                  tracking-[0.15em]
                  font-medium
                  text-[var(--qc-text)]
                  mb-6
                "
              >
                Contact
              </h4>

              <div className="space-y-4">

                <a
                  href="mailto:hello@questioncraft.ai"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  hello@questioncraft.ai
                </a>

                <a
                  href="#"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  LinkedIn
                </a>

                <a
                  href="#"
                  className="block text-[15px] text-[var(--qc-text-secondary)] hover:text-[var(--qc-text)]"
                >
                  GitHub
                </a>

              </div>

            </div>

          </div>

          <div
            className="
              mt-20
              pt-8
              border-t
              border-[var(--qc-divider)]

              flex
              flex-col
              md:flex-row
              justify-between
              gap-4
            "
          >

            <p
              className="
                text-sm
                text-[var(--qc-text-muted)]
              "
            >
              © 2026 QuestionCraft. All rights reserved.
            </p>

            <p
              className="
                text-sm
                text-[var(--qc-text-muted)]
              "
            >
              Designed for modern education.
            </p>

          </div>

        </div>

      </Container>

    </footer>
  );
}