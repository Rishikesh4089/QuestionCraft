import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info";
}

const variants = {
  default:
    "bg-slate-100 text-slate-600 border border-slate-200",

  success:
    "bg-emerald-50 text-emerald-700 border border-emerald-200",

  warning:
    "bg-amber-50 text-amber-700 border border-amber-200",

  danger:
    "bg-red-50 text-red-600 border border-red-200",

  info:
    "bg-blue-50 text-blue-700 border border-blue-200",
};

export function Badge({
  children,
  variant = "default",
  className,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center",
        "px-2.5 py-1",
        "rounded-full",
        "text-xs font-medium",
        "whitespace-nowrap",
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

export default Badge;