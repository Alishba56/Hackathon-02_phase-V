'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { CheckSquare, Sparkles, Moon, Zap, ArrowRight, Star, Users, TrendingUp, Shield } from 'lucide-react';
import { ThemeToggle } from '@/components/layout/theme-toggle';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background overflow-hidden">
      {/* Animated Background with Purple-Cyan Gradient */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent/10" />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/30 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-float-slow" />
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-primary/20 rounded-full blur-3xl animate-pulse-slow" />
      </div>

      <div className="container mx-auto px-4">
        {/* Header */}
        <header className="flex justify-between items-center py-6 mb-12 animate-fade-in-down">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold gradient-text">
              TaskFlow
            </span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/login">
              <Button variant="ghost" className="hover:bg-primary/10 transition-all duration-300">Login</Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-gradient-to-r from-primary to-accent hover:shadow-glow-lg transition-all duration-300 hover:scale-105">
                Get Started
              </Button>
            </Link>
          </div>
        </header>

        {/* Hero Section */}
        <div className="text-center max-w-5xl mx-auto mb-24 ">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary/20 to-accent/20 border border-primary/30 text-primary text-sm font-medium mb-8 animate-fade-in backdrop-blur-sm">
            <Sparkles className="h-4 w-4 animate-spin-slow" />
            <span>✨ Modern & Best-in-Class UI</span>
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-8xl font-bold mb-8 leading-tight animate-fade-in-up">
            <span className="bg-gradient-to-r gradient-text animate-gradient-x from-foreground via-foreground to-foreground/70 bg-clip-text text-transparent">
              Task Management,
            </span>
            <br />
            <span className="gradient-text animate-gradient-x">
              Beautifully Reimagined
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-muted-foreground mb-12 max-w-3xl mx-auto leading-relaxed animate-fade-in-up animation-delay-200">
            Experience premium task management with a stunning interface,
            smooth animations, and delightful interactions. Built for productivity enthusiasts.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in-up animation-delay-300">
            <Link href="/signup">
              <Button size="lg" className="text-lg px-10 py-6 bg-gradient-to-r from-primary to-accent hover:shadow-glow-lg transition-all duration-300 hover:scale-105 group">
                Start Free Trial
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="text-lg px-10 py-6 border-2 border-primary/50 hover:bg-primary/5 hover:border-primary transition-all duration-300 hover:scale-105">
                Sign In
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-8 max-w-3xl mx-auto pt-8 border-t border-primary/20 animate-fade-in animation-delay-500">
            <div className="group hover:scale-110 transition-transform duration-300">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">10K+</div>
              <div className="text-sm text-muted-foreground">Active Users</div>
            </div>
            <div className="group hover:scale-110 transition-transform duration-300">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">50K+</div>
              <div className="text-sm text-muted-foreground">Tasks Completed</div>
            </div>
            <div className="group hover:scale-110 transition-transform duration-300">
              <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">4.9★</div>
              <div className="text-sm text-muted-foreground">User Rating</div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="max-w-6xl mx-auto mb-24">
          <div className="text-center mb-16 animate-fade-in-up">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Everything you need to stay productive
            </h2>
            <p className="text-xl text-muted-foreground">
              Powerful features wrapped in a beautiful interface
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow hover:border-primary/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-100">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow">
                <Zap className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-primary transition-colors">Lightning Fast</h3>
              <p className="text-muted-foreground leading-relaxed">
                Optimistic updates and smooth animations make every interaction feel instant and responsive.
              </p>
            </div>

            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow-cyan hover:border-accent/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-200">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-accent to-primary flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow-cyan">
                <Moon className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-accent transition-colors">Dark Mode</h3>
              <p className="text-muted-foreground leading-relaxed">
                Beautiful light and dark themes that adapt to your system preferences automatically.
              </p>
            </div>

            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow hover:border-primary/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-300">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow">
                <CheckSquare className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-primary transition-colors">Intuitive Design</h3>
              <p className="text-muted-foreground leading-relaxed">
                Clean, modern interface inspired by the best productivity apps in the world.
              </p>
            </div>

            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow-cyan hover:border-accent/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-100">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-accent to-primary flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow-cyan">
                <Shield className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-accent transition-colors">Secure & Private</h3>
              <p className="text-muted-foreground leading-relaxed">
                Your data is encrypted and secure. We never share your information with third parties.
              </p>
            </div>

            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow hover:border-primary/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-200">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow">
                <Users className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-primary transition-colors">Team Collaboration</h3>
              <p className="text-muted-foreground leading-relaxed">
                Work together seamlessly with real-time updates and shared task lists.
              </p>
            </div>

            <div className="group p-8 rounded-2xl border border-primary/20 bg-card/50 backdrop-blur-sm hover:shadow-glow-cyan hover:border-accent/50 transition-all duration-500 hover:-translate-y-2 animate-fade-in-up animation-delay-300">
              <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-accent to-primary flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-glow-cyan">
                <TrendingUp className="h-7 w-7 " />
              </div>
              <h3 className="text-2xl font-semibold mb-3 group-hover:text-accent transition-colors">Analytics & Insights</h3>
              <p className="text-muted-foreground leading-relaxed">
                Track your productivity with detailed analytics and actionable insights.
              </p>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-4xl mx-auto mb-24 animate-fade-in-up">
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-primary via-primary to-accent p-12 md:p-16 text-center shadow-glow-lg animate-gradient-x">
            <div className="absolute inset-0 bg-grid-white/10" />
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-float-slow" />
            <div className="relative z-10">
              <h2 className="text-4xl md:text-5xl font-bold  mb-6 animate-fade-in-up">
                Ready to boost your productivity?
              </h2>
              <p className="text-xl  mb-8 max-w-2xl mx-auto animate-fade-in-up animation-delay-100">
                Join thousands of users who have transformed their workflow with TaskFlow
              </p>
              <Link href="/signup">
                <Button size="lg" variant="secondary" className="text-lg px-10 py-6 bg-white text-black hover:bg-white/90 shadow-xl hover:scale-105 transition-all duration-300 group animate-fade-in-up animation-delay-200">
                  Get Started for Free
                  <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-primary/20 py-12 mt-24 animate-fade-in">
          <div className="flex flex-col md:flex-row justify-center items-center gap-6">
            <p className="text-sm text-muted-foreground">
              © 2026 TaskFlow. All rights reserved.
            </p>

          </div>
        </footer>
      </div>
    </div>
  );
}
