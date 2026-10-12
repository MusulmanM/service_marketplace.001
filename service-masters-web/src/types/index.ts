export type UserRole = 'master' | 'client' | 'admin';

export type OrderStatus =
  | 'new'
  | 'accepted'
  | 'en_route'
  | 'on_site'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'rejected'
  | 'pending_review';

export interface User {
  id: string;
  phone: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  avatar?: string | null;
  phone_number?: string;
  user_type?: UserRole;
  profile?: {
    first_name?: string;
    last_name?: string;
    avatar?: string | null;
  };
}

export interface MasterProfile {
  id: string;
  user?: User | string;
  name?: string;
  bio?: string;
  description?: string;
  rating: number;
  reviews_count: number;
  categories: string[] | { id: string; name: string }[];
  cities: string[] | { id: string; name: string }[];
  is_online?: boolean;
  is_available?: boolean;
  is_verified: boolean;
  completed_jobs?: number;
}

export interface OrderPhoto {
  id: string;
  image: string;
  kind: 'before' | 'after';
  created_at: string;
}

export interface OrderReport {
  id: string;
  summary: string;
  labor_cost: number;
  parts_cost: number;
  total: number;
  warranty_days: number;
  created_at: string;
}

export interface Order {
  id: string;
  number: string;
  status: OrderStatus;
  title: string;
  description?: string;
  address: string;
  district?: string;
  client_name: string;
  client_phone?: string;
  price?: number | string;
  scheduled_at?: string;
  created_at: string;
  updated_at: string;
  photos?: OrderPhoto[];
  report?: OrderReport | null;
  master?: string | MasterProfile | null;
}

export interface LoginPayload {
  phone: string;
  password: string;
}

export interface RegisterPayload {
  phone: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  role?: UserRole;
}

export interface TokenResponse {
  access: string;
  refresh: string;
  user?: User;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
