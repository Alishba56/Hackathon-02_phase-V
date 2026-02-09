'use client';

import * as React from 'react';
import { Priority } from '@/types';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface PrioritySelectProps {
  value: Priority;
  onValueChange: (value: Priority) => void;
  disabled?: boolean;
}

const priorityOptions: { value: Priority; label: string; description: string }[] = [
  { value: 'low', label: 'Low', description: 'Low priority task' },
  { value: 'medium', label: 'Medium', description: 'Normal priority task' },
  { value: 'high', label: 'High', description: 'High priority task' },
  { value: 'urgent', label: 'Urgent', description: 'Urgent priority task' },
];

export function PrioritySelect({ value, onValueChange, disabled }: PrioritySelectProps) {
  return (
    <Select value={value} onValueChange={onValueChange} disabled={disabled}>
      <SelectTrigger className="w-full bg-black">
        <SelectValue placeholder="Select priority" />
      </SelectTrigger>
      <SelectContent className='bg-black'>
        {priorityOptions.map((option) => (
          <SelectItem key={option.value} value={option.value} >
            <div className="flex items-center gap-2 ">
              <span className={`priority-indicator priority-${option.value}`} />
              <span>{option.label}</span>
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
