'use client';

import * as React from 'react';
import { Calendar, Clock, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface DateTimePickerProps {
  value: string | null | undefined;
  onChange: (value: string | null) => void;
  label: string;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export function DateTimePicker({
  value,
  onChange,
  label,
  placeholder = 'Select date and time',
  disabled = false,
  className,
}: DateTimePickerProps) {
  // Convert ISO string to datetime-local format (YYYY-MM-DDTHH:mm)
  const formatForInput = (isoString: string | null | undefined): string => {
    if (!isoString) return '';
    try {
      const date = new Date(isoString);
      // Format: YYYY-MM-DDTHH:mm
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    } catch {
      return '';
    }
  };

  // Convert datetime-local format to ISO string
  const formatForOutput = (localString: string): string | null => {
    if (!localString) return null;
    try {
      const date = new Date(localString);
      return date.toISOString();
    } catch {
      return null;
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const localValue = e.target.value;
    onChange(formatForOutput(localValue));
  };

  const handleClear = () => {
    onChange(null);
  };

  return (
    <div className={cn('space-y-2', className)}>
      <Label className="text-sm font-medium">{label}</Label>
      <div className="relative">
        <div className="absolute left-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-muted-foreground pointer-events-none">
          <Calendar className="h-4 w-4" />
          <Clock className="h-4 w-4" />
        </div>
        <Input
          type="datetime-local"
          value={formatForInput(value)}
          onChange={handleChange}
          disabled={disabled}
          className="pl-16 pr-9"
        />
        {value && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
            aria-label={`Clear ${label.toLowerCase()}`}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}
