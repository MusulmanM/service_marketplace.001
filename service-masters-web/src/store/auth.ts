import { create } from 'zustand';
import type { RegisterPayload, User } from '@/types';
import { authApi } from '@/api/endpoints';
import { normalizeUser } from '@/api/normalize';

interface AuthState {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (phone: string, password: string) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => void;
  fetchMe: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  loading: true,
  isAuthenticated: !!localStorage.getItem('access_token'),

  login: async (phone, password) => {
    const { data } = await authApi.login({ phone, password });
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    let user: User;
    if (data.user) {
      user = normalizeUser(data.user);
    } else {
      const me = await authApi.me();
      user = me.data;
    }
    set({ user, isAuthenticated: true, loading: false });
    return user;
  },

  register: async (payload) => {
    await authApi.register(payload);
    return get().login(payload.phone.trim().replace(/\s+/g, ''), payload.password);
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    set({ user: null, isAuthenticated: false });
  },

  fetchMe: async () => {
    try {
      const { data } = await authApi.me();
      set({ user: data, isAuthenticated: true, loading: false });
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      set({ user: null, isAuthenticated: false, loading: false });
    }
  },

  setUser: (user) => set({ user }),
}));
