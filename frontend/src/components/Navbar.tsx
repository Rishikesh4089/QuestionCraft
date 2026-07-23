import Button from "@/components/ui/Button";
import Container from "@/components/ui/Container";

interface NavbarProps {
    onLogin: () => void;
    onGetStarted: () => void;
}

const links = [
  {
    label: "Features",
    href: "#features",
  },
  {
    label: "How it Works",
    href: "#how-it-works",
  },
  {
    label: "Pricing",
    href: "#pricing",
  },
  {
    label: "About",
    href: "#about",
  },
];

export default function Navbar({ onGetStarted }: NavbarProps) {
  return (
    <header
      className="
        sticky
        top-0
        z-50
        bg-[var(--qc-bg)]/90
        backdrop-blur-md
        border-b
        border-[var(--qc-divider)]
      "
    >
      <Container>

        <nav className="h-20 flex items-center justify-between">

          {/* Logo */}

          <a
            href="/"
            className="flex items-center gap-3 group"
          >
            <img
              src="/logo.png"
              alt="QuestionCraft"
              className="
                w-15
                h-15
                transition-transform
                duration-300
                group-hover:rotate-[-6deg]
                group-hover:scale-105
              "
            />

            <span
              className="
                text-[28px]
                font-semibold
                tracking-[-0.03em]
                text-[var(--qc-text)]
              "
            >
              QuestionCraft
            </span>
          </a>

          {/* Navigation */}

          <div className="hidden lg:flex items-center gap-35">

            {links.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="
                  text-[17px]
                  font-medium
                  text-[var(--qc-text-secondary)]
                  hover:text-[var(--qc-text)]
                  transition-colors
                "
              >
                {item.label}
              </a>
            ))}

          </div>

          {/* CTA */}

          <div className="flex items-center">


            <Button
              onClick={onGetStarted}
              className="text-[15px] font-medium"
            >
              Start Creating
            </Button>

          </div>

        </nav>

      </Container>
    </header>
  );
}