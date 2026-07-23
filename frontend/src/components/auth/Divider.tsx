interface DividerProps {
  text?: string;
}

export default function Divider({
  text = "or continue with",
}: DividerProps) {
  return (
    <div className="relative my-8">

      <div
        className="
          absolute
          inset-0
          flex
          items-center
        "
      >
        <div
          className="
            w-full
            border-t
            border-[var(--qc-divider)]
          "
        />
      </div>

      <div className="relative flex justify-center">

        <span
          className="
            bg-white

            px-5

            text-sm

            font-medium

            text-[var(--qc-text-muted)]
          "
        >
          {text}
        </span>

      </div>

    </div>
  );
}