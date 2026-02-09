// Shared type definitions for the application

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface RecurrenceRule {
  frequency: 'daily' | 'weekly' | 'monthly' | 'custom';
  interval: number;
  end_date?: string | null;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority: Priority;
  tags: string[];
  due_date?: string | null;
  remind_at?: string | null;
  recurrence_rule?: RecurrenceRule | null;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

export type Theme = 'light' | 'dark';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

export interface Pagination {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}