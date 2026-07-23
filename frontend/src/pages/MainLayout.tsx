import { useState } from "react";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import SearchPanel from "@/components/SearchPanel";

import Dashboard from "@/pages/Dashboard/Dashboard";
import GeneratePaper from "@/pages/GeneratePaper";
import PaperHistory from "@/pages/PaperHistory";
import Settings from "@/pages/Settings";
import FAQ from "@/pages/FAQ";

import { useAuth } from "@/contexts/AuthContext";
import { DashboardPage } from "@/components/dashboard/DashboardSidebar";

export default function MainLayout() {
  const [currentPage, setCurrentPage] =
    useState<DashboardPage>("home");

  const [showSearch, setShowSearch] =
    useState(false);

  const { user, signOut } = useAuth();

  const displayName =
    user?.user_metadata?.full_name ||
    user?.email?.split("@")[0] ||
    "User";

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (err) {
      console.error(err);
    }
  };

  const handleNavigate = (page: DashboardPage) => {
    setCurrentPage(page);
  };

  const renderPage = () => {
    switch (currentPage) {
      case "home":
        return (
          <Dashboard
            onNavigate={setCurrentPage}
          />
        );

      case "generate":
        return <GeneratePaper />;

      case "history":
        return <PaperHistory />;

      case "settings":
        return <Settings />;

      case "faq":
        return <FAQ />;

      default:
        return (
          <Dashboard
            onNavigate={setCurrentPage}
          />
        );
    }
  };

  return (
    <>
      <DashboardLayout
        activePage={currentPage}
        userName={displayName}
        onNavigate={handleNavigate}
        onLogout={handleSignOut}
        onSearch={() => setShowSearch(true)}
      >
        {renderPage()}
      </DashboardLayout>

      {showSearch && (
        <SearchPanel
          onClose={() =>
            setShowSearch(false)
          }
        />
      )}
    </>
  );
}