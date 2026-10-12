import type { User, UserRole } from '@/types';

/** Normalize Django /me/ (and nested) payloads into the frontend User shape. */
export function normalizeUser(raw: Record<string, unknown> | User): User {
  const data = raw as Record<string, unknown>;
  const profile = (data.profile as Record<string, unknown> | undefined) || undefined;

  const role = (data.role || data.user_type || 'master') as UserRole;
  const phone = String(data.phone || data.phone_number || '');
  const first =
    String(data.first_name || profile?.first_name || '') || '';
  const last = String(data.last_name || profile?.last_name || '') || '';
  const avatar =
    (data.avatar as string | null | undefined) ??
    (profile?.avatar as string | null | undefined) ??
    null;

  return {
    id: String(data.id),
    phone,
    first_name: first,
    last_name: last,
    role,
    avatar,
    phone_number: phone,
    user_type: role,
    profile: profile as User['profile'],
  };
}
