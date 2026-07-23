import { ReactNode } from "react";

interface AuthLayoutProps {
  illustration: ReactNode;
  children: ReactNode;
}

export default function AuthLayout({
  illustration,
  children,
}: AuthLayoutProps) {
  return (
    <main
      className="
        min-h-screen
        overflow-y-auto
        bg-[var(--qc-black)]
      "
    >
      <div
        className="
          h-full

          grid

          lg:grid-cols-[55%_45%]
        "
      >
        {/* LEFT */}

        <section
          className="
            hidden
            lg:flex

            items-center
            justify-center

            bg-[var(--qc-bg)]

            p-10
          "
        >
          {illustration}
        </section>

        {/* RIGHT */}

        <section
          className="
            flex
            items-center
            justify-center

            bg-[var(--qc-black)]

            p-10
          "
        >
          {children}
        </section>
      </div>
    </main>
  );
}