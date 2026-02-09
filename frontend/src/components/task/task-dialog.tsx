'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PrioritySelect } from '@/components/task/priority-select';
import { TagsInput } from '@/components/task/tags-input';
import { DateTimePicker } from '@/components/task/date-time-picker';
import type { Task, Priority } from '@/types';

interface TaskDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskCreated: (task: Task) => void;
  task?: Task;
}

export function TaskDialog({ open, onOpenChange, onTaskCreated, task }: TaskDialogProps) {
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [priority, setPriority] = useState<Priority>(task?.priority || 'medium');
  const [tags, setTags] = useState<string[]>(task?.tags || []);
  const [dueDate, setDueDate] = useState<string | null>(task?.due_date || null);
  const [remindAt, setRemindAt] = useState<string | null>(task?.remind_at || null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('No authentication token found');
      }

      if (task) {
        // Update existing task
        const response = await fetch(`${apiUrl}/api/tasks/${task.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            title,
            description,
            priority,
            tags,
            due_date: dueDate,
            remind_at: remindAt,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to update task');
        }

        const updatedTask = await response.json();
        onTaskCreated(updatedTask);
      } else {
        // Create new task
        const response = await fetch(`${apiUrl}/api/tasks`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            title,
            description,
            priority,
            tags,
            due_date: dueDate,
            remind_at: remindAt,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to create task');
        }

        const newTask = await response.json();
        onTaskCreated(newTask);
      }

      setIsLoading(false);

      // Reset form
      setTitle('');
      setDescription('');
      setPriority('medium');
      setTags([]);
      setDueDate(null);
      setRemindAt(null);
    } catch (error) {
      console.error('Error saving task:', error);
      alert('Failed to save task. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] border-primary/20 bg-card/95 backdrop-blur-sm animate-fade-in-up">
        <DialogHeader>
          <DialogTitle className="text-2xl gradient-text">{task ? 'Edit Task' : 'Create New Task'}</DialogTitle>
          <DialogDescription className="text-white">
            {task ? 'Update your task details below.' : 'Add a new task to your list. Fill in the details below.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-1 pb-2">
            <div className="grid gap-2 animate-fade-in-up animation-delay-100">
              <Label htmlFor="title" className="text-sm text-white font-medium">Title</Label>
              <Input
                id="title"
                placeholder="Enter task title..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                autoFocus
                className="text-black focus-visible:ring-primary border-primary/20"
              />
            </div>

            <div className="grid gap-2 animate-fade-in-up animation-delay-200">
              <Label htmlFor="description" className="text-sm text-white font-medium">Description (Optional)</Label>
              <Input
                id="description"
                placeholder="Add more details..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="text-black focus-visible:ring-primary border-primary/20"
              />
            </div>

            <div className="grid gap-2 animate-fade-in-up animation-delay-300">
              <Label htmlFor="priority" className="text-sm text-white font-medium">Priority</Label>
              <PrioritySelect
                value={priority}
                onValueChange={setPriority}
                disabled={isLoading}
              />
            </div>

            <div className="grid gap-2 animate-fade-in-up animation-delay-400">
              <Label htmlFor="tags" className="text-sm text-white font-medium">Tags (Optional)</Label>
              <TagsInput
                value={tags}
                onChange={setTags}
                placeholder="Add tags (press Enter or comma)"
                maxTags={10}
                disabled={isLoading}
              />
            </div>

            <div className="grid gap-2 animate-fade-in-up animation-delay-500">
              <DateTimePicker
                value={dueDate}
                onChange={setDueDate}
                label="Due Date (Optional)"
                placeholder="Select due date"
                disabled={isLoading}
              />
            </div>

            <div className="grid gap-2 animate-fade-in-up animation-delay-600">
              <DateTimePicker
                value={remindAt}
                onChange={setRemindAt}
                label="Reminder (Optional)"
                placeholder="Select reminder time"
                disabled={isLoading}
              />
            </div>
          </div>

          <DialogFooter className="gap-2 animate-fade-in-up animation-delay-700">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="hover:bg-primary/10 text-white border-primary/20"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading || !title.trim()}
              className="bg-gradient-to-r text-white from-primary to-accent hover:shadow-glow-lg transition-all duration-300 hover:scale-105"
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Saving...
                </span>
              ) : (
                task ? 'Update Task' : 'Create Task'
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
