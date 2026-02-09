'use client';

import { useState } from 'react';
import { User as UserType } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

interface SettingsFormProps {
  user?: UserType;
}

export default function SettingsForm({ user }: SettingsFormProps) {
  const [notifications, setNotifications] = useState(true);
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [language, setLanguage] = useState('en');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // In a real implementation, this would make an API call to update settings
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Handle success
      alert('Settings updated successfully!');
    } catch (error) {
      // Handle error
      console.error('Error updating settings:', error);
      alert('Failed to update settings');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full border-primary/20 bg-card/50 backdrop-blur-sm shadow-glow animate-fade-in-up">
      <CardHeader>
        <CardTitle className="text-2xl gradient-text">Account Settings</CardTitle>
        <CardDescription>
          Configure your account preferences
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="space-y-6">
            <div className="space-y-4 animate-fade-in-up animation-delay-100">
              <h3 className="text-lg font-semibold gradient-text">Preferences</h3>

              <div className="flex items-center justify-between p-4 rounded-lg bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/20 hover:border-primary/30 transition-all duration-300">
                <div className="space-y-0.5">
                  <Label htmlFor="notifications" className="text-base font-medium">
                    Email Notifications
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Receive notifications via email
                  </p>
                </div>
                <Switch
                  id="notifications"
                  checked={notifications}
                  onCheckedChange={setNotifications}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="language" className="text-sm font-medium">Language</Label>
                <select
                  id="language"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="block w-full rounded-lg border border-primary/20 bg-background px-4 py-2.5 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-300"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="theme" className="text-sm font-medium">Theme</Label>
                <select
                  id="theme"
                  value={theme}
                  onChange={(e) => setTheme(e.target.value as 'light' | 'dark')}
                  className="block w-full rounded-lg border border-primary/20 bg-background px-4 py-2.5 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary transition-all duration-300"
                >
                  <option value="light">Light</option>
                  <option value="dark">Dark</option>
                </select>
              </div>
            </div>

            <div className="space-y-4 animate-fade-in-up animation-delay-200">
              <h3 className="text-lg font-semibold text-destructive">Danger Zone</h3>

              <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 backdrop-blur-sm">
                <h4 className="font-medium text-destructive">Delete Account</h4>
                <p className="mt-1 text-sm text-muted-foreground">
                  Permanently remove your account and all associated data.
                </p>
                <Button variant="destructive" size="sm" className="mt-3 hover:shadow-glow transition-all duration-300">
                  Delete Account
                </Button>
              </div>
            </div>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="bg-gradient-to-r from-primary to-accent hover:shadow-glow-lg transition-all duration-300 hover:scale-105 animate-fade-in-up animation-delay-300"
          >
            {isLoading ? (
              <span className="flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                Saving...
              </span>
            ) : (
              'Save Settings'
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}