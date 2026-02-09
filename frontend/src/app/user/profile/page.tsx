'use client';

import { useEffect, useState } from 'react';
import ProfileForm from '@/components/user/profile-form';

export default function ProfilePage() {
  const [user, setUser] = useState<{ name: string; email: string } | null>(null);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }
  }, []);

  return (
    <div className="space-y-6 animate-fade-in-up">
      <div>
        <h1 className="text-4xl font-bold gradient-text mb-2">Profile</h1>
        <p className="text-muted-foreground">
          Manage your account information
        </p>
      </div>

      <div className="grid gap-8">
        <ProfileForm user={user} />
      </div>
    </div>
  );
}