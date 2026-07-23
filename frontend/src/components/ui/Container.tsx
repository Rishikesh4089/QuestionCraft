import { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
  size?: "default" | "wide" | "narrow";
}

const widths = {
  narrow: "max-w-4xl",
  default: "max-w-[1500px]",
  wide: "max-w-[1440px]",
};

export default function Container({
  children,
  className,
  size = "default",
  ...props
}: ContainerProps) {
  return (
    <div
      className={cn(
        "w-full mx-auto",
        widths[size],

        // Responsive horizontal padding
        "px-6 sm:px-8 lg:px-12 xl:px-10",

        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}