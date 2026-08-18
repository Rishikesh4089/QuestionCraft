// src/components/ui/Button.tsx

import {
  ButtonHTMLAttributes,
  ReactNode,
} from "react";

import { cn } from "@/lib/utils";

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;

  variant?:
    | "primary"
    | "secondary"
    | "outline"
    | "ghost"
    | "danger";

  size?: "sm" | "md" | "lg";

  leftIcon?: ReactNode;
  rightIcon?: ReactNode;

  loading?: boolean;
}

const variants = {
  primary:
    "bg-[var(--qc-primary)] text-white hover:brightness-95",

  secondary:
    "bg-[var(--qc-text)] text-white hover:opacity-90",

  outline:
    "border border-[var(--qc-divider)] bg-white text-[var(--qc-text)] hover:bg-[var(--qc-bg)]",

  ghost:
    "bg-transparent text-[var(--qc-text)] hover:bg-[var(--qc-bg)]",

  danger:
    "bg-red-600 text-white hover:bg-red-700",
};

const sizes = {
  sm: "h-9 px-3 text-sm",

  md: "h-11 px-5 text-base",

  lg: "h-12 px-6 text-[17px]",
};

export default function Button({
  children,

  variant = "primary",

  size = "md",

  leftIcon,

  rightIcon,

  loading = false,

  disabled,

  className,

  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        // Base
        "inline-flex items-center justify-center gap-2",

        "rounded-xl",

        "font-medium",

        "transition-all duration-200",

        // Focus
        "focus:outline-none",

        "focus:ring-2",

        "focus:ring-[var(--qc-primary)]/30",

        // Disabled
        "disabled:opacity-50",

        "disabled:cursor-not-allowed",

        // Variant
        variants[variant],

        // Size
        sizes[size],

        className
      )}
      {...props}
    >
      {loading ? (
        <>
          <span
            className="
              w-4
              h-4

              border-2
              border-current
              border-t-transparent

              rounded-full

              animate-spin
            "
          />

          <span>Loading...</span>
        </>
      ) : (
        <>
          {leftIcon && (
            <span className="flex items-center shrink-0">
              {leftIcon}
            </span>
          )}

          <span>
            {children}
          </span>

          {rightIcon && (
            <span className="flex items-center shrink-0">
              {rightIcon}
            </span>
          )}
        </>
      )}
    </button>
  );
}