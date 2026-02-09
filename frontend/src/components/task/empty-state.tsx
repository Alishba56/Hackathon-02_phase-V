import { Button } from '@/components/ui/button';
import { CheckSquare, Plus } from 'lucide-react';

interface EmptyStateProps {
  onAddTask: () => void;
}

export function EmptyState({ onAddTask }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-4 animate-fade-in">
      <div className="h-24 w-24 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mb-6 shadow-glow animate-pulse-slow">
        <CheckSquare className="h-12 w-12 text-primary" />
      </div>

      <h2 className="text-3xl font-bold mb-3 gradient-text animate-fade-in-up animation-delay-100">No tasks yet</h2>
      <p className="text-muted-foreground text-center mb-8 max-w-md animate-fade-in-up animation-delay-200">
        Get started by creating your first task. Stay organized and productive with our beautiful task management interface.
      </p>

      <Button
        size="lg"
        onClick={onAddTask}
        className="bg-gradient-to-r from-primary to-accent hover:shadow-glow-lg transition-all duration-300 hover:scale-105 animate-fade-in-up animation-delay-300"
      >
        <Plus className="h-5 w-5 mr-2" />
        Create Your First Task
      </Button>
    </div>
  );
}
