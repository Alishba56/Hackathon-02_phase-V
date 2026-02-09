'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { CheckSquare, LayoutDashboard, ListTodo, User } from 'lucide-react';
import { cn } from '@/lib/utils';

const sidebarItems = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    title: 'My Tasks',
    href: '/dashboard',
    icon: ListTodo,
  },
  {
    title: 'Profile',
    href: '/user/profile',
    icon: User,
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-primary/20 bg-card/30 backdrop-blur-sm animate-slide-in-right">
      {/* Logo */}
      <div className="p-6 border-b border-primary/20">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-xl font-bold gradient-text">TaskFlow</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {sidebarItems.map((item, index) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group animate-fade-in-up',
                isActive
                  ? 'bg-gradient-to-r from-primary/20 to-accent/20 text-primary border border-primary/30 shadow-glow'
                  : 'hover:bg-primary/10 text-muted-foreground hover:text-foreground'
              )}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <Icon
                className={cn(
                  'h-5 w-5 transition-transform duration-300',
                  isActive ? 'text-primary' : 'group-hover:scale-110'
                )}
              />
              <span className="font-medium">{item.title}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-primary/20">
        <div className="p-4 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 border border-primary/20 animate-fade-in">
          <p className="text-sm font-semibold mb-1 gradient-text">Pro Tip</p>
          <p className="text-xs text-muted-foreground">
            Use keyboard shortcuts to boost your productivity!
          </p>
        </div>
      </div>
    </aside>
  );
}
