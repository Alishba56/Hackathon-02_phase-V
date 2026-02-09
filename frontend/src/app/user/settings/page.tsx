'use client';

import { useEffect, useState } from 'react';
import SettingsForm from '@/components/user/settings-form';
import { User } from '@/types';

export default function SettingsPage() {
  const [user, setUser] = useState<User | undefined>(undefined);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-4xl font-bold gradient-text mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account settings and preferences
        </p>
      </div>

      <div className="grid gap-8">
        <SettingsForm user={user} />
      </div>
    </div>
  );
}