import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, FolderKanban, AlertTriangle, ScrollText, Users, Settings } from 'lucide-react';

const Layout = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/escalations', icon: AlertTriangle, label: 'Escalations', badge: 0 },
    { path: '/audit', icon: ScrollText, label: 'Audit Log' },
    { path: '/team', icon: Users, label: 'Team' },
  ];

  return (
    <div className="flex h-screen bg-bg">
      {/* Sidebar */}
      <aside className="w-60 bg-surface border-r border-border flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-border">
          <h1 className="text-lg font-semibold text-text-primary">Tech Sarathi</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-md mb-2 transition-colors ${
                  isActive
                    ? 'bg-primary/10 text-primary border-l-3 border-primary'
                    : 'text-text-secondary hover:bg-surface-raised hover:text-text-primary'
                }`}
              >
                <Icon size={20} />
                <span className="text-sm font-medium">{item.label}</span>
                {item.badge !== undefined && item.badge > 0 && (
                  <span className="ml-auto bg-danger text-white text-xs px-2 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm font-semibold">
              PM
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-text-primary">Project Manager</p>
              <p className="text-xs text-text-secondary">pm@techsarathi.com</p>
            </div>
            <Settings size={18} className="text-text-secondary cursor-pointer hover:text-text-primary" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default Layout;
