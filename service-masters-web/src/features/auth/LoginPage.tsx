import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { isAxiosError } from 'axios';
import { useAuthStore } from '@/store/auth';
import type { UserRole } from '@/types';
import { Wrench } from 'lucide-react';

const inputClass =
  'w-full h-12 px-4 rounded-xl bg-surface-container-lowest border border-outline-variant/40 text-on-surface placeholder:text-outline focus:outline-none focus:ring-2 focus:ring-primary/40';

const labelClass =
  'block text-xs font-semibold text-on-surface-variant mb-1.5 uppercase tracking-wider';

function redirectForRole(role: string | undefined) {
  if (role === 'master' || role === 'admin') return '/orders';
  return '/orders';
}

function formatApiErrors(err: unknown, fallback: string): string {
  if (!isAxiosError(err) || !err.response?.data) return fallback;
  const data = err.response.data as Record<string, unknown> | string;
  if (typeof data === 'string') return data || fallback;
  if (typeof data.detail === 'string') return data.detail;
  const parts: string[] = [];
  for (const [key, value] of Object.entries(data)) {
    if (key === 'detail') continue;
    const messages = Array.isArray(value) ? value : [value];
    for (const msg of messages) {
      if (typeof msg === 'string') parts.push(msg);
    }
  }
  return parts.length ? parts.join(' ') : fallback;
}

export default function LoginPage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const login = useAuthStore((s) => s.login);
  const register = useAuthStore((s) => s.register);

  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [role, setRole] = useState<UserRole>('client');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const switchMode = (next: 'login' | 'register') => {
    setMode(next);
    setError('');
    setPassword('');
    setPasswordConfirm('');
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const normalizedPhone = phone.trim().replace(/\s+/g, '');
    try {
      if (mode === 'register') {
        if (password !== passwordConfirm) {
          setError(t('password_mismatch'));
          return;
        }
        const user = await register({
          phone: normalizedPhone,
          password,
          password_confirm: passwordConfirm,
          first_name: firstName,
          last_name: lastName,
          role,
        });
        navigate(redirectForRole(user.role));
      } else {
        const user = await login(normalizedPhone, password);
        navigate(redirectForRole(user.role));
      }
    } catch (err) {
      setError(formatApiErrors(err, t('error_generic')));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full flex flex-col items-center justify-center px-6 py-8 bg-surface">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center mb-4 shadow-lg">
            <Wrench className="text-on-primary" size={32} />
          </div>
          <h1 className="text-2xl font-bold text-on-surface tracking-tight">{t('app_name')}</h1>
          <p className="text-sm text-on-surface-variant mt-1">
            {mode === 'register' ? t('register_subtitle') : t('login_subtitle')}
          </p>
        </div>

        <div className="flex mb-5 p-1 rounded-xl bg-surface-container">
          <button
            type="button"
            onClick={() => switchMode('login')}
            className={`flex-1 h-10 rounded-lg text-sm font-semibold transition-colors ${
              mode === 'login'
                ? 'bg-primary text-on-primary shadow-sm'
                : 'text-on-surface-variant'
            }`}
          >
            {t('login')}
          </button>
          <button
            type="button"
            onClick={() => switchMode('register')}
            className={`flex-1 h-10 rounded-lg text-sm font-semibold transition-colors ${
              mode === 'register'
                ? 'bg-primary text-on-primary shadow-sm'
                : 'text-on-surface-variant'
            }`}
          >
            {t('register')}
          </button>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          {mode === 'register' && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className={labelClass}>{t('first_name')}</label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    autoComplete="given-name"
                    className={inputClass}
                  />
                </div>
                <div>
                  <label className={labelClass}>{t('last_name')}</label>
                  <input
                    type="text"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    autoComplete="family-name"
                    className={inputClass}
                  />
                </div>
              </div>

              <div>
                <label className={labelClass}>{t('role')}</label>
                <div className="flex gap-2">
                  {(['client', 'master'] as const).map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setRole(r)}
                      className={`flex-1 h-11 rounded-xl text-sm font-semibold transition-colors ${
                        role === r
                          ? 'bg-primary text-on-primary shadow-sm'
                          : 'bg-surface-container-lowest border border-outline-variant/40 text-on-surface-variant'
                      }`}
                    >
                      {t(r === 'client' ? 'role_client' : 'role_master')}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          <div>
            <label className={labelClass}>{t('phone')}</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+998 90 123 45 67"
              autoComplete="tel"
              className={inputClass}
              required
            />
          </div>
          <div>
            <label className={labelClass}>{t('password')}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={mode === 'register' ? 'new-password' : 'current-password'}
              className={inputClass}
              required
              minLength={mode === 'register' ? 8 : undefined}
            />
          </div>

          {mode === 'register' && (
            <div>
              <label className={labelClass}>{t('password_confirm')}</label>
              <input
                type="password"
                value={passwordConfirm}
                onChange={(e) => setPasswordConfirm(e.target.value)}
                autoComplete="new-password"
                className={inputClass}
                required
                minLength={8}
              />
            </div>
          )}

          {error && (
            <p className="text-sm text-error bg-error-container/50 px-3 py-2 rounded-lg whitespace-pre-wrap">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full h-12 rounded-xl bg-primary text-on-primary font-semibold shadow-md hover:bg-primary-container transition-colors disabled:opacity-60"
          >
            {loading ? t('loading') : mode === 'register' ? t('register') : t('login')}
          </button>
        </form>

        <p className="text-center text-sm text-on-surface-variant mt-4">
          {mode === 'login' ? (
            <>
              {t('no_account')}{' '}
              <button
                type="button"
                onClick={() => switchMode('register')}
                className="font-semibold text-primary"
              >
                {t('register')}
              </button>
            </>
          ) : (
            <>
              {t('have_account')}{' '}
              <button
                type="button"
                onClick={() => switchMode('login')}
                className="font-semibold text-primary"
              >
                {t('login')}
              </button>
            </>
          )}
        </p>

        <div className="flex justify-center gap-2 mt-6">
          {(['ru', 'en', 'uz'] as const).map((lng) => (
            <button
              key={lng}
              type="button"
              onClick={() => {
                i18n.changeLanguage(lng);
                localStorage.setItem('lang', lng);
              }}
              className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${
                i18n.language === lng
                  ? 'bg-primary text-on-primary'
                  : 'bg-surface-container text-on-surface-variant'
              }`}
            >
              {lng}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
