/**
 * Authentication state management using Zustand.
 */

import { create } from 'zustand';
import { supabase, signInWithGoogle, signInWithGitHub, signOut } from '../services/supabase';
import type { User } from '../types';

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;

  // Actions
  initialize: () => Promise<void>;
  login: () => Promise<void>;
  loginWithGitHub: () => Promise<void>;
  logout: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  
  initialize: async () => {
    try {
      set({ isLoading: true });
      
      // Get current session
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.user) {
        const user: User = {
          id: session.user.id,
          email: session.user.email,
          name: session.user.user_metadata?.full_name,
          avatar_url: session.user.user_metadata?.avatar_url,
        };
        set({ user, isAuthenticated: true });
      }
      
      // Listen for auth changes
      supabase.auth.onAuthStateChange((_event, session) => {
        if (session?.user) {
          const user: User = {
            id: session.user.id,
            email: session.user.email,
            name: session.user.user_metadata?.full_name,
            avatar_url: session.user.user_metadata?.avatar_url,
          };
          set({ user, isAuthenticated: true });
        } else {
          set({ user: null, isAuthenticated: false });
        }
      });
    } catch (error) {
      console.error('Auth initialization error:', error);
    } finally {
      set({ isLoading: false });
    }
  },
  
  login: async () => {
    try {
      await signInWithGoogle();
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  loginWithGitHub: async () => {
    try {
      await signInWithGitHub();
    } catch (error) {
      console.error('GitHub login error:', error);
      throw error;
    }
  },
  
  logout: async () => {
    try {
      await signOut();
      set({ user: null, isAuthenticated: false });
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },
  
  setUser: (user) => {
    set({ user, isAuthenticated: !!user });
  },
}));

