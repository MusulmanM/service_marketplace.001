import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { LogOut, BadgeCheck, ChevronRight, Settings } from 'lucide-react';

export default function ProfilePage() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  const name = user
    ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.phone
    : 'Master';

  return (
    <div className="min-h-full bg-surface">
      <header className="pt-safe bg-surface-container-lowest border-b border-outline-variant/20">
        <div className="px-4 py-5 flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-primary text-on-primary flex items-center justify-center text-2xl font-bold">
            {name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <h1 className="text-lg font-bold truncate">{name}</h1>
              <BadgeCheck size={18} className="text-primary shrink-0" />
            </div>
            <p className="text-sm text-on-surface-variant">{user?.phone}</p>
            <p className="text-xs font-semibold text-primary mt-0.5 uppercase">{user?.role || 'master'}</p>
          </div>
        </div>
      </header>

      <main className="px-4 py-4 space-y-3">
        <div className="bg-surface-container-lowest rounded-2xl shadow-sm divide-y divide-outline-variant/15">
          {['Services & Prices', 'Work Zones', 'Payout Card', 'Documents'].map((item) => (
            <button
              key={item}
              className="w-full flex items-center justify-between px-4 py-3.5 text-left hover:bg-surface-container-low"
            >
              <span className="font-medium text-sm">{item}</span>
              <ChevronRight size={18} className="text-outline" />
            </button>
          ))}
        </div>

        <div className="bg-surface-container-lowest rounded-2xl shadow-sm p-4">
          <div className="flex items-center gap-2 mb-3">
            <Settings size={16} className="text-on-surface-variant" />
            <span className="text-sm font-semibold">Language</span>
          </div>
          <div className="flex gap-2">
            {(['ru', 'en', 'uz'] as const).map((lng) => (
              <button
                key={lng}
                onClick={() => {
                  i18n.changeLanguage(lng);
                  localStorage.setItem('lang', lng);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-bold uppercase ${
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

        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="w-full h-12 rounded-xl bg-error-container text-error font-semibold flex items-center justify-center gap-2"
        >
          <LogOut size={18} />
          {t('logout')}
        </button>
      </main>
    </div>
  );
}
