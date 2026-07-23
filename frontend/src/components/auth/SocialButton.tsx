import { ReactNode } from "react";

interface SocialButtonProps {
  icon: ReactNode;
  children: ReactNode;
  onClick?: () => void;
}

export default function SocialButton({
  icon,
  children,
  onClick,
}: SocialButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="
        w-full

        h-14

        rounded-full

        bg-white

        border
        border-[var(--qc-border)]

        flex
        items-center
        justify-center
        gap-3

        text-[15px]
        font-medium

        text-[var(--qc-text)]

        transition-all
        duration-200

        hover:bg-[#FAF8F4]
        hover:border-[#F76C00]
        hover:shadow-md

        active:scale-[0.98]
      "
    >
      <span
        className="
          flex
          items-center
          justify-center

          w-5
          h-5
        "
      >
        {icon}
      </span>

      <span>{children}</span>
    </button>
  );
}