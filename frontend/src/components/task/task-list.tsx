'use client';

import { TaskItem } from './task-item';
import type { Task } from '@/types';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: (tasks: Task[]) => void;
}

export function TaskList({ tasks, onTaskUpdate }: TaskListProps) {
  const handleToggleComplete = async (taskId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${apiUrl}/api/tasks/${taskId}/complete`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to toggle task completion');
      }

      const updatedTask = await response.json();

      // Update local state with the response from backend
      const updatedTasks = tasks.map(task =>
        task.id === taskId ? updatedTask : task
      );
      onTaskUpdate(updatedTasks);
    } catch (error) {
      console.error('Error toggling task completion:', error);
      alert('Failed to update task. Please try again.');
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${apiUrl}/api/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      // Remove task from local state
      const updatedTasks = tasks.filter(task => task.id !== taskId);
      onTaskUpdate(updatedTasks);
    } catch (error) {
      console.error('Error deleting task:', error);
      alert('Failed to delete task. Please try again.');
    }
  };

  const handleEditTask = (updatedTask: Task) => {
    // Update local state with edited task (API call is handled in TaskDialog)
    const updatedTasks = tasks.map(task =>
      task.id === updatedTask.id ? updatedTask : task
    );
    onTaskUpdate(updatedTasks);
  };

  // Separate completed and incomplete tasks
  const incompleteTasks = tasks.filter(task => !task.completed);
  const completedTasks = tasks.filter(task => task.completed);

  return (
    <div className="space-y-8">
      {/* Incomplete Tasks */}
      {incompleteTasks.length > 0 && (
        <div className="animate-fade-in-up">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-1 w-1 rounded-full bg-primary animate-pulse" />
            <h2 className="text-sm font-semibold gradient-text uppercase tracking-wide">
              Active Tasks ({incompleteTasks.length})
            </h2>
            <div className="flex-1 h-px bg-gradient-to-r from-primary/20 to-transparent" />
          </div>
          <div className="space-y-3">
            {incompleteTasks.map((task, index) => (
              <div key={task.id} style={{ animationDelay: `${index * 50}ms` }}>
                <TaskItem
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onDelete={handleDeleteTask}
                  onEdit={handleEditTask}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="animate-fade-in-up animation-delay-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-1 w-1 rounded-full bg-accent animate-pulse" />
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              Completed ({completedTasks.length})
            </h2>
            <div className="flex-1 h-px bg-gradient-to-r from-accent/20 to-transparent" />
          </div>
          <div className="space-y-3">
            {completedTasks.map((task, index) => (
              <div key={task.id} style={{ animationDelay: `${index * 50}ms` }}>
                <TaskItem
                  task={task}
                  onToggleComplete={handleToggleComplete}
                  onDelete={handleDeleteTask}
                  onEdit={handleEditTask}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
