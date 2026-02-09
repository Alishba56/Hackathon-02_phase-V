'use client';

import { ReactNode, useEffect, useState } from 'react';
import { ThemeToggle } from '@/components/layout/theme-toggle';
import { Sidebar } from '@/components/layout/sidebar';
import { CheckSquare, LogOut, User, Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  useEffect(() => {
    // Check if user is logged in
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Redirect to login if not authenticated
      router.push('/login');
    }
  }, [router]);

  const handleLogout = () => {
    // Clear auth data
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    // Redirect to login
    router.push('/login');
    router.refresh();
  };

  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Animated Background with Purple-Cyan Gradient */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-float-slow" />
      </div>

      <div className="flex h-screen">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="sticky top-0 z-50 w-full border-b border-primary/20 bg-background/80 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60 animate-fade-in-down">
            <div className="flex h-16 items-center justify-between px-6">
              {/* Mobile Menu Button */}
              <Button variant="ghost" size="icon" className="lg:hidden">
                <Menu className="h-5 w-5" />
              </Button>

              {/* Mobile Logo */}
              <Link href="/" className="flex lg:hidden items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-glow">
                  <CheckSquare className="h-5 w-5 text-white" />
                </div>
                <span className="text-lg font-bold gradient-text">TaskFlow</span>
              </Link>

              {/* Right Side */}
              <div className="flex items-center gap-3 ml-auto">
                {user && (
                  <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-primary/20 backdrop-blur-sm animate-fade-in">
                    <User className="h-4 w-4 text-primary" />
                    <span className="text-sm font-medium">{user.name}</span>
                  </div>
                )}
                <ThemeToggle />
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="gap-2 hover:bg-primary/10 hover:text-primary transition-all duration-300"
                  title="Logout"
                >
                  <LogOut className="h-5 w-5" />
                  <span className="hidden md:inline">Logout</span>
                </Button>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto">
            <div className="container mx-auto px-6 py-8">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
