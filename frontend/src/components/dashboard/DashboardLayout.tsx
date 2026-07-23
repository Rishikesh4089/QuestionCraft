import { ReactNode } from "react";

import DashboardSidebar, {
  DashboardPage,
} from "./DashboardSidebar";
import DashboardTopbar from "./DashboardTopbar";

interface DashboardLayoutProps {
  activePage: DashboardPage;
  userName: string;

  children: ReactNode;

  onNavigate: (page: DashboardPage) => void;
  onLogout: () => void;

  onSearch?: () => void;
  onNotifications?: () => void;
  onProfile?: () => void;
}

export default function DashboardLayout({
  activePage,
  userName,
  children,
  onNavigate,
  onLogout,
  onSearch,
  onNotifications,
  onProfile,
}: DashboardLayoutProps) {
  return (
    <div className="flex min-h-screen bg-[var(--qc-bg)]">

      {/* Sidebar */}

      <DashboardSidebar
        activePage={activePage}
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      {/* Main Content */}

      <div className="flex flex-1 flex-col min-w-0">

        <DashboardTopbar
          userName={userName}
          onSearch={onSearch}
          onNotifications={onNotifications}
          onProfile={onProfile}
        />

        <main
          className="
            flex-1
            overflow-y-auto
            p-8
          "
        >
          {children}
        </main>

      </div>

    </div>
  );
}