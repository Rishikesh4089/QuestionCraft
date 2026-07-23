import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";
import Container from "./Container";

interface SectionProps extends HTMLAttributes<HTMLElement> {
  container?: "narrow" | "default" | "wide";
  dividerTop?: boolean;
  dividerBottom?: boolean;
  background?: string;
  fullWidth?: boolean;
}

export default function Section({
  children,
  className,
  container = "default",
  dividerTop = false,
  dividerBottom = false,
  background,
  fullWidth = false,
  style,
  ...props
}: SectionProps) {
  return (
    <section
      className={cn(
        "relative py-28 lg:py-36",
        dividerTop && "border-t border-[var(--qc-divider)]",
        dividerBottom && "border-b border-[var(--qc-divider)]",
        className
      )}
      style={{
        background,
        ...style,
      }}
      {...props}
    >
      {fullWidth ? (
        children
      ) : (
        <Container size={container}>
          {children}
        </Container>
      )}
    </section>
  );
}