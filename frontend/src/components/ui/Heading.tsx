import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface HeadingProps extends Omit<HTMLAttributes<HTMLDivElement>, "title"> {
  eyebrow?: string;
  title: React.ReactNode;
  description?: React.ReactNode;

  align?: "left" | "center";

  size?: "sm" | "md" | "lg";

  maxWidth?: "sm" | "md" | "lg" | "full";
}

const titleSizes = {
  sm: "text-3xl md:text-4xl",
  md: "text-4xl md:text-5xl",
  lg: "text-5xl md:text-6xl lg:text-7xl",
};

const widths = {
  sm: "max-w-2xl",
  md: "max-w-3xl",
  lg: "max-w-4xl",
  full: "max-w-none",
};

export default function Heading({
  eyebrow,
  title,
  description,
  align = "left",
  size = "md",
  maxWidth = "lg",
  className,
  ...props
}: HeadingProps) {
  const center = align === "center";

  return (
    <div
      className={cn(
        widths[maxWidth],
        center && "mx-auto text-center",
        className
      )}
      {...props}
    >
      {eyebrow && (
        <p
          className="
            mb-5
            text-sm
            font-medium
            tracking-[0.18em]
            uppercase
            text-[var(--qc-primary)]
          "
        >
          {eyebrow}
        </p>
      )}

      <h2
        className={cn(
          titleSizes[size],

          "font-semibold",

          "leading-[1.05]",

          "tracking-[-0.04em]",

          "text-[var(--qc-text)]"
        )}
      >
        {title}
      </h2>

      {description && (
        <p
          className="
            mt-7
            max-w-2xl
            text-lg
            leading-8
            text-[var(--qc-text-secondary)]
          "
        >
          {description}
        </p>
      )}
    </div>
  );
}