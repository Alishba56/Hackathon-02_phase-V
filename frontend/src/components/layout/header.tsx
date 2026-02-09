'use client';

import { MainNav } from './main-nav';
import { MobileNav } from './mobile-nav';
import { ThemeToggle } from './theme-toggle';
import { Button } from '@/components/ui/button';
import { User, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export function Header() {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  useEffect(() => {
    // Check if user is logged in
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  const handleLogout = () => {
    // Clear auth data
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Redirect to login
    router.push('/login');
    router.refresh();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <MobileNav />
        <div className="mr-4 hidden lg:flex">
          <MainNav />
        </div>
        <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
          <div className="w-full flex-1 md:w-auto md:flex-none">
            {/* Search or other content can go here */}
          </div>
          <nav className="flex items-center gap-2">
            <ThemeToggle />
            {user && (
              <>
                <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-md bg-muted">
                  <User className="h-4 w-4" />
                  <span className="text-sm font-medium">{user.name}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden md:inline">Logout</span>
                </Button>
              </>
            )}
            {!user && (
              <Button variant="ghost" size="icon" aria-label="User profile">
                <User className="h-5 w-5" />
              </Button>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}
