import { FileText, PlusCircle, History, Settings, HelpCircle, LogOut, Search, Home } from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onNavigate: (page: string) => void;
  onSignOut: () => void;
}

export default function Sidebar({ currentPage, onNavigate, onSignOut }: SidebarProps) {
  const menuItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'generate', label: 'Generate Paper', icon: PlusCircle },
    { id: 'history', label: 'Previous Papers', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
  ];

  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen">
      <div className="p-6 border-b border-slate-200">
        <div className="flex items-center space-x-2">
          <img
        src="/logo.png"
        alt="QuestionCraft Logo"
        className="w-17 h-17 object-contain"
      />
          <span className="text-xl font-bold text-slate-800">QuestionCraft</span>
        </div>
      </div>

      <div className="p-4">
        <button
          onClick={() => onNavigate('search')}
          className="w-full flex items-center space-x-3 px-4 py-2 text-slate-600 hover:bg-slate-50 rounded-lg transition-colors"
        >
          <Search className="w-5 h-5" />
          <span>Search</span>
        </button>
      </div>

      <nav className="flex-1 px-4 py-2">
        <div className="space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                currentPage === item.id
                  ? 'bg-slate-800 text-white'
                  : 'text-slate-700 hover:bg-slate-50'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <div className="p-4 border-t border-slate-200">
        <button
          onClick={onSignOut}
          className="w-full flex items-center space-x-3 px-4 py-3 text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </div>
  );
}
