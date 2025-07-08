import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from './ui/Button';
import { Sun, Moon, Menu } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Navbar() {
  const location = useLocation();
  const [isDark, setIsDark] = React.useState(() => {
    // Check localStorage and system preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      return savedTheme === 'dark';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

  React.useEffect(() => {
    // Apply theme on mount and theme change
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const isActiveRoute = (path) => location.pathname === path;

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/chatbot', label: 'AI Chatbot' },
    { path: '/voice-transcriber', label: 'Voice Transcriber' },
    { path: '/call-simulator', label: 'Call Simulator' },
    { path: '/data-manager', label: 'Data Manager' },
  ];

  const navLinkClass = (isActive) =>
    cn(
      'relative px-3 py-2 text-sm font-medium transition-colors hover:text-primary',
      {
        'text-primary dark:text-primary-foreground': isActive,
        'text-muted-foreground hover:text-foreground dark:text-muted-foreground dark:hover:text-foreground': !isActive,
      }
    );

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <span className="font-bold text-foreground">Call Insights</span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            {navItems.map(({ path, label }) => (
              <Link
                key={path}
                to={path}
                className={navLinkClass(isActiveRoute(path))}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <Button
            variant="ghost"
            size="sm"
            className="w-9 px-0"
            onClick={toggleTheme}
          >
            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="md:hidden w-9 px-0"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            <Menu className="h-4 w-4" />
          </Button>
        </div>
      </div>
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-border">
          <nav className="flex flex-col space-y-1 p-2">
            {navItems.map(({ path, label }) => (
              <Link
                key={path}
                to={path}
                className={cn(
                  'px-3 py-2 text-sm rounded-md transition-colors',
                  isActiveRoute(path)
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50'
                )}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
} 