import { api } from './client';
import { normalizeUser } from './normalize';
import type {
  LoginPayload,
  RegisterPayload,
  TokenResponse,
  User,
  Order,
  MasterProfile,
  Paginated,
} from '@/types';

export const authApi = {
  login: ({ phone, password }: LoginPayload) =>
    api.post<TokenResponse>('/users/token/', {
      phone,
      phone_number: phone.trim().replace(/\s+/g, ''),
      password,
    }),
  register: (data: RegisterPayload) => {
    const phone = data.phone.trim().replace(/\s+/g, '');
    return api.post<User>('/users/register/', {
      phone,
      phone_number: phone,
      password: data.password,
      password_confirm: data.password_confirm,
      first_name: data.first_name?.trim() || '',
      last_name: data.last_name?.trim() || '',
      role: data.role || 'client',
      user_type: data.role || 'client',
    });
  },
  me: async () => {
    const res = await api.get('/users/me/');
    return { ...res, data: normalizeUser(res.data as User) };
  },
  updateMe: (data: Partial<User>) => api.patch<User>('/users/me/', data),
};

export const mastersApi = {
  list: (params?: { category?: string; city?: string }) =>
    api.get<Paginated<MasterProfile> | MasterProfile[]>('/masters/', { params }),
  me: () => api.get<MasterProfile>('/masters/me/'),
  updateMe: (data: Partial<MasterProfile>) =>
    api.patch<MasterProfile>('/masters/me/', data),
  createMe: (data: Partial<MasterProfile>) =>
    api.post<MasterProfile>('/masters/me/', data),
};

export const ordersApi = {
  list: (params?: { status?: string }) =>
    api.get<Paginated<Order> | Order[]>('/orders/', { params }),
  get: (id: number | string) => api.get<Order>(`/orders/${id}/`),
  create: (data: Partial<Order>) => api.post<Order>('/orders/', data),
  updateStatus: (id: number | string, status: string) =>
    api.patch<Order>(`/orders/${id}/status/`, { status }),
  uploadPhoto: (id: number | string, formData: FormData) =>
    api.post(`/orders/${id}/photos/`, formData),
  submitReport: (id: number | string, data: Record<string, unknown>) =>
    api.post(`/orders/${id}/report/`, data),
  submitReview: (id: number | string, data: Record<string, unknown>) =>
    api.post(`/orders/${id}/review/`, data),
};
