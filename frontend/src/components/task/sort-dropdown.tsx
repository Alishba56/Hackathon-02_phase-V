'use client';

import * as React from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';

export type SortField = 'created_at' | 'title' | 'priority' | 'due_date';
export type SortOrder = 'asc' | 'desc';

interface SortState {
  field: SortField;
  order: SortOrder;
}

interface SortDropdownProps {
  value: SortState;
  onChange: (value: SortState) => void;
}

const sortOptions: { value: SortField; label: string }[] = [
  { value: 'created_at', label: 'Date Created' },
  { value: 'title', label: 'Title' },
  { value: 'priority', label: 'Priority' },
  { value: 'due_date', label: 'Due Date' },
];

export function SortDropdown({ value, onChange }: SortDropdownProps) {
  const toggleOrder = () => {
    onChange({
      ...value,
      order: value.order === 'asc' ? 'desc' : 'asc',
    });
  };

  const handleFieldChange = (field: SortField) => {
    onChange({ ...value, field });
  };

  return (
    <div className="flex items-center gap-2">
      <Select value={value.field} onValueChange={handleFieldChange}>
        <SelectTrigger className="w-[180px]">
          <ArrowUpDown className="h-4 w-4 mr-2" />
          <SelectValue placeholder="Sort by..." />
        </SelectTrigger>
        <SelectContent>
          {sortOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        variant="outline"
        size="icon"
        onClick={toggleOrder}
        aria-label={`Sort ${value.order === 'asc' ? 'ascending' : 'descending'}`}
      >
        {value.order === 'asc' ? (
          <ArrowUp className="h-4 w-4" />
        ) : (
          <ArrowDown className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
