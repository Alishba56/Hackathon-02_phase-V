'use client';

import { ThemeProvider } from '@/contexts/theme-provider';

interface ProvidersProps {
  children: React.ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ThemeProvider defaultTheme="light" storageKey="taskflow-theme">
      {children}
    </ThemeProvider>
  );
}