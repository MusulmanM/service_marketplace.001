import { useTranslation } from 'react-i18next';
import { TrendingUp, Wallet, Hourglass } from 'lucide-react';

export default function EarningsPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-full bg-surface">
      <header className="sticky top-0 z-20 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="px-4 py-4">
          <h1 className="text-xl font-bold text-on-surface">{t('earnings')}</h1>
          <p className="text-sm text-on-surface-variant">This month</p>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        {/* Hero card */}
        <div className="rounded-2xl bg-inverse-surface text-inverse-on-surface p-5 shadow-md">
          <p className="text-xs uppercase tracking-wider opacity-70">{t('total_earnings')}</p>
          <p className="text-3xl font-bold mt-1">12,480,000 <span className="text-base font-medium opacity-80">UZS</span></p>
          <div className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded-full bg-secondary/20 text-secondary-container text-xs font-semibold">
            <TrendingUp size={14} /> +18.4%
          </div>

          <div className="grid grid-cols-2 gap-2 mt-4">
            <div className="rounded-xl bg-white/10 p-3">
              <div className="flex items-center gap-1 text-xs opacity-80">
                <Hourglass size={14} /> {t('pending_escrow')}
              </div>
              <p className="font-bold mt-1">680,000</p>
            </div>
            <div className="rounded-xl bg-white/10 p-3">
              <div className="flex items-center gap-1 text-xs opacity-80">
                <Wallet size={14} /> {t('ready_to_disburse')}
              </div>
              <p className="font-bold mt-1">11,800,000</p>
            </div>
          </div>

          <button className="w-full h-11 mt-4 rounded-xl bg-primary text-on-primary font-semibold">
            Request Payout
          </button>
        </div>

        {/* KPI */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: 'Completion Rate', value: '99.2%' },
            { label: 'Client Rating', value: '4.96 ★' },
            { label: 'On-Time Arrival', value: '96.8%' },
            { label: 'Warranty Claims', value: '0.4%' },
          ].map((k) => (
            <div key={k.label} className="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm">
              <p className="text-xs text-on-surface-variant">{k.label}</p>
              <p className="text-xl font-bold text-on-surface mt-1">{k.value}</p>
            </div>
          ))}
        </div>

        <p className="text-xs text-center text-on-surface-variant pt-2">
          Hook these cards to real payout / stats API when ready.
        </p>
      </main>
    </div>
  );
}
