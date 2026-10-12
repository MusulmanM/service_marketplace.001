import { NavLink } from 'react-router-dom';
import { ClipboardList, CalendarDays, BarChart3, UserCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';

const items = [
  { to: '/orders', icon: ClipboardList, key: 'orders' },
  { to: '/schedule', icon: CalendarDays, key: 'schedule' },
  { to: '/earnings', icon: BarChart3, key: 'earnings' },
  { to: '/profile', icon: UserCircle, key: 'profile' },
];

export default function BottomNav() {
  const { t } = useTranslation();

  return (
    <nav className="fixed bottom-0 inset-x-0 z-50 pb-safe bg-surface-container-lowest/90 backdrop-blur-xl border-t border-outline-variant/30">
      <div className="flex justify-around items-center h-16 max-w-lg mx-auto px-2">
        {items.map(({ to, icon: Icon, key }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex flex-col items-center justify-center flex-1 h-12 gap-0.5 transition-colors',
                isActive ? 'text-primary' : 'text-on-surface-variant'
              )
            }
          >
            {({ isActive }) => (
              <>
                <span
                  className={clsx(
                    'flex items-center justify-center w-12 h-7 rounded-full transition-colors',
                    isActive && 'bg-primary/10'
                  )}
                >
                  <Icon size={22} strokeWidth={isActive ? 2.4 : 2} />
                </span>
                <span className="text-[11px] font-semibold">{t(key)}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
