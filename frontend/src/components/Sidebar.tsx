// src/components/layout/Sidebar.tsx
import { FileText, PlusCircle, History, Settings, HelpCircle, LogOut, Search, Home, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  onSignOut: () => void;
}

const NAV_ITEMS = [
  { id: "home",     label: "Home",            icon: Home,        description: "Dashboard overview" },
  { id: "generate", label: "Generate Paper",   icon: PlusCircle,  description: "Create a new paper" },
  { id: "history",  label: "My Papers",        icon: History,     description: "View past papers" },
  { id: "settings", label: "Settings",         icon: Settings,    description: "Account settings" },
  { id: "faq",      label: "Help & FAQ",       icon: HelpCircle,  description: "Get support" },
];

export default function Sidebar({ currentPage, onNavigate, onSignOut }: SidebarProps) {
  const { user } = useAuth();
  const initials = user?.email?.slice(0, 2).toUpperCase() ?? "QC";

  return (
    <aside className="w-60 shrink-0 bg-slate-950 text-slate-300 flex flex-col h-screen">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <img src="/logo.png" alt="QuestionCraft" className="w-8 h-8 object-contain rounded" />
          <div>
            <p className="text-sm font-bold text-white tracking-tight">QuestionCraft</p>
            <p className="text-[10px] text-slate-500 tracking-wide uppercase">AI Paper Generator</p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="px-3 py-3">
        <button
          onClick={() => onNavigate("search")}
          className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-all text-sm"
        >
          <Search className="w-4 h-4 shrink-0" />
          <span>Search papers...</span>
          <kbd className="ml-auto text-[10px] bg-slate-800 border border-slate-700 rounded px-1.5 py-0.5">⌘K</kbd>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-2 space-y-0.5 overflow-y-auto">
        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest px-3 pb-2 pt-1">Menu</p>
        {NAV_ITEMS.map((item) => {
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all text-sm group relative",
                active
                  ? "bg-slate-800 text-white"
                  : "text-slate-400 hover:bg-slate-800/60 hover:text-white",
              )}
            >
              {/* Active bar */}
              {active && (
                <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-white rounded-r-full" />
              )}
              <item.icon className={cn("w-4 h-4 shrink-0", active && "text-white")} />
              <span className="font-medium">{item.label}</span>
              {active && <ChevronRight className="w-3 h-3 ml-auto text-slate-500" />}
            </button>
          );
        })}
      </nav>

      {/* User + sign out */}
      <div className="px-3 py-4 border-t border-slate-800 space-y-1">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-slate-900">
          <div className="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {initials}
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-xs font-medium text-white truncate">{user?.email}</p>
            <p className="text-[10px] text-slate-500">Free plan</p>
          </div>
        </div>
        <button
          onClick={onSignOut}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:bg-red-950 hover:text-red-400 transition-all text-sm"
        >
          <LogOut className="w-4 h-4 shrink-0" />
          <span className="font-medium">Sign out</span>
        </button>
      </div>
    </aside>
  );
}