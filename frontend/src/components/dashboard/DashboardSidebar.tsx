import {
  LayoutDashboard,
  FileText,
  FolderOpen,
  Library,
  History,
  BarChart3,
  CreditCard,
  Settings,
  HelpCircle,
  LogOut,
} from "lucide-react";

export type DashboardPage =
  | "home"
  | "generate"
  | "documents"
  | "question-bank"
  | "history"
  | "analytics"
  | "billing"
  | "settings"
  | "faq";

interface DashboardSidebarProps {
  activePage: DashboardPage;
  onNavigate: (page: DashboardPage) => void;
  onLogout: () => void;
}

const navigation = [
  {
    id: "home",
    label: "Dashboard",
    icon: LayoutDashboard,
  },
  {
    id: "generate",
    label: "Generate Paper",
    icon: FileText,
  },
  {
    id: "documents",
    label: "Documents",
    icon: FolderOpen,
  },
  {
    id: "question-bank",
    label: "Question Bank",
    icon: Library,
  },
  {
    id: "history",
    label: "History",
    icon: History,
  },
  {
    id: "analytics",
    label: "Analytics",
    icon: BarChart3,
  },
  {
    id: "billing",
    label: "Billing",
    icon: CreditCard,
  },
  {
    id: "settings",
    label: "Settings",
    icon: Settings,
  },
  {
    id: "faq",
    label: "Help",
    icon: HelpCircle,
  },
] as const;

export default function DashboardSidebar({
  activePage,
  onNavigate,
  onLogout,
}: DashboardSidebarProps) {
  return (
    <aside
      className="
        w-72
        bg-white
        border-r
        border-[var(--qc-divider)]
        h-screen
        sticky
        top-0
        flex
        flex-col
      "
    >
      {/* Logo */}

      <div className="px-8 py-8 border-b border-[var(--qc-divider)]">

        <div className="flex items-center gap-3">

          <img
            src="/logo.png"
            alt="QuestionCraft"
            className="w-10 h-10"
          />

          <div>

            <h1
              className="
                text-xl
                font-bold
                tracking-tight
                text-[var(--qc-text)]
              "
            >
              QuestionCraft
            </h1>

            <p
              className="
                text-sm
                text-[var(--qc-text-secondary)]
              "
            >
              AI Assessment Platform
            </p>

          </div>

        </div>

      </div>

      {/* Navigation */}

      <nav className="flex-1 px-4 py-6 space-y-2">

        {navigation.map((item) => {
          const Icon = item.icon;

          const active = activePage === item.id;

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                w-full
                flex
                items-center
                gap-4
                px-4
                py-3
                rounded-2xl
                transition-all
                ${
                  active
                    ? "bg-[var(--qc-primary)] text-white shadow-md"
                    : "text-[var(--qc-text-secondary)] hover:bg-[var(--qc-bg)]"
                }
              `}
            >
              <Icon className="w-5 h-5" />

              <span className="font-medium">
                {item.label}
              </span>

            </button>
          );
        })}

      </nav>

      {/* Logout */}

      <div className="p-4 border-t border-[var(--qc-divider)]">

        <button
          onClick={onLogout}
          className="
            w-full
            flex
            items-center
            gap-4
            px-4
            py-3
            rounded-2xl
            text-red-500
            hover:bg-red-50
            transition-colors
          "
        >
          <LogOut className="w-5 h-5" />

          <span className="font-medium">
            Sign Out
          </span>

        </button>

      </div>

    </aside>
  );
}