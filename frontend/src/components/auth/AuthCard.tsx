import { ReactNode } from "react";

interface AuthCardProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export default function AuthCard({
  title,
  subtitle,
  children,
}: AuthCardProps) {
  return (
    <div
    className="
        w-full
        max-w-[560px]

        bg-white

        rounded-[32px]

        px-14
        py-10

        shadow-2xl
    "
>
      {/* Logo */}

      <div className="flex justify-center">

        <img
          src="/logo.png"
          alt="QuestionCraft"
          className="w-16 h-16"
        />

      </div>

      {/* Heading */}

      <div className="mt-4 text-center">

        <h1
          className="
            text-4xl

            font-semibold

            tracking-[-0.03em]

            text-[var(--qc-text)]
          "
        >
          {title}
        </h1>

        <p
          className="
            mt-3

            text-[15px]

            text-[var(--qc-text-secondary)]
          "
        >
          {subtitle}
        </p>

      </div>

      <div className="mt-6">

        {children}

      </div>

    </div>
  );
}