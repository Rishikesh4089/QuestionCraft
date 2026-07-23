import {
  Bell,
  Search,
  ChevronDown,
} from "lucide-react";

interface DashboardTopbarProps {
  userName: string;
  onSearch?: () => void;
  onNotifications?: () => void;
  onProfile?: () => void;
}

export default function DashboardTopbar({
  userName,
  onSearch,
  onNotifications,
  onProfile,
}: DashboardTopbarProps) {
  return (
    <header
      className="
        sticky
        top-0
        z-20
        bg-[var(--qc-bg)]/90
        backdrop-blur-md
        border-b
        border-[var(--qc-divider)]
      "
    >
      <div className="h-20 px-8 flex items-center justify-between">

        {/* Search */}

        <button
          onClick={onSearch}
          className="
            w-[420px]
            h-12
            rounded-xl
            border
            border-[var(--qc-divider)]
            bg-white
            flex
            items-center
            gap-3
            px-4
            text-[var(--qc-text-secondary)]
            hover:border-[var(--qc-primary)]
            transition-colors
          "
        >
          <Search className="w-5 h-5" />

          <span className="text-sm">
            Search papers, templates, documents...
          </span>
        </button>

        {/* Right */}

        <div className="flex items-center gap-4">

          <button
            onClick={onNotifications}
            className="
              w-11
              h-11
              rounded-xl
              border
              border-[var(--qc-divider)]
              bg-white
              flex
              items-center
              justify-center
              hover:border-[var(--qc-primary)]
              transition-colors
            "
          >
            <Bell className="w-5 h-5" />
          </button>

          <button
            onClick={onProfile}
            className="
              flex
              items-center
              gap-3
              rounded-xl
              border
              border-[var(--qc-divider)]
              bg-white
              px-3
              py-2
              hover:border-[var(--qc-primary)]
              transition-colors
            "
          >
            <div
              className="
                w-10
                h-10
                rounded-full
                bg-[var(--qc-primary)]
                text-white
                flex
                items-center
                justify-center
                font-semibold
              "
            >
              {userName.charAt(0).toUpperCase()}
            </div>

            <div className="text-left">

              <p
                className="
                  text-sm
                  font-semibold
                  text-[var(--qc-text)]
                "
              >
                {userName}
              </p>

              <p
                className="
                  text-xs
                  text-[var(--qc-text-secondary)]
                "
              >
                Teacher
              </p>

            </div>

            <ChevronDown className="w-4 h-4" />

          </button>

        </div>

      </div>
    </header>
  );
}