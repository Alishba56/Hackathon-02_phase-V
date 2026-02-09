// Better Auth client integration
// This file sets up the authentication client for the application

import { createAuthClient } from 'better-auth/client';

// Initialize the auth client
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:8002',
});

// Export auth functions
export const { signIn, signUp, signOut } = authClient;

// Helper to get session
export const getSession = async () => {
  // This would typically call an API endpoint to get the current session
  // For now, return a placeholder
  return null;
};

// Define types for auth
export type Session = {
  user: {
    id: string;
    email: string;
    name: string;
  };
} | null;