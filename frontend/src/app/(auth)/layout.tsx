import type { ReactNode } from 'react'
import Link from 'next/link'
import { CheckSquare } from 'lucide-react'

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background overflow-hidden">
      {/* Animated Background with Purple-Cyan Gradient */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent/10" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/30 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-float-slow" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse-slow" />
      </div>

      <div className="mx-auto w-full max-w-md px-4">
        {/* Logo */}
        <Link href="/" className="flex items-center justify-center gap-2 my-10 animate-fade-in-down">
          <span className="text-2xl font-bold gradient-text">
            TaskFlow
          </span>
        </Link>

        {/* Auth Card */}
        <div className="backdrop-blur-sm bg-card/50 border border-primary/20 rounded-2xl shadow-glow p-8 animate-fade-in-up">
          {children}
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground my-10 animate-fade-in">
          © 2026 TaskFlow. All rights reserved.
        </p>
      </div>
    </div>
  )
}