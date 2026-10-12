import { useTranslation } from 'react-i18next';
import { CalendarDays } from 'lucide-react';

export default function SchedulePage() {
  const { t } = useTranslation();

  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const today = 3; // demo highlight

  return (
    <div className="min-h-full bg-surface">
      <header className="sticky top-0 z-20 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="px-4 py-4">
          <h1 className="text-xl font-bold text-on-surface">{t('schedule')}</h1>
          <p className="text-sm text-on-surface-variant">Agenda view</p>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        <div className="flex gap-2 overflow-x-auto pb-1">
          {days.map((d, i) => (
            <button
              key={d}
              className={`min-w-[52px] py-2.5 rounded-xl flex flex-col items-center ${
                i === today
                  ? 'bg-primary text-on-primary shadow-md'
                  : 'bg-surface-container-lowest text-on-surface-variant'
              }`}
            >
              <span className="text-[11px] font-medium">{d}</span>
              <span className="text-lg font-bold">{21 + i}</span>
            </button>
          ))}
        </div>

        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <CalendarDays size={18} className="text-primary" />
            <span className="font-semibold">Today overview</span>
          </div>
          <p className="text-sm text-on-surface-variant">
            Connect your backend schedule endpoint to show real time slots and jobs here.
            Block-time and conflict modals from the design kit can be wired next.
          </p>
        </div>

        <div className="space-y-2">
          {[
            { time: '09:00 – 10:30', title: 'AC Deep Clean', client: 'Jasur A.', status: 'Done' },
            { time: '11:00 – 12:45', title: 'Circuit Breaker', client: 'Elena S.', status: 'Active' },
            { time: '14:15 – 16:00', title: '3-Phase Panel', client: 'Bakhtiyor N.', status: 'Queued' },
          ].map((job) => (
            <div
              key={job.time}
              className="bg-surface-container-lowest rounded-xl p-3.5 shadow-sm flex justify-between gap-3"
            >
              <div>
                <p className="text-xs font-semibold text-on-surface-variant">{job.time}</p>
                <p className="font-semibold text-on-surface mt-0.5">{job.title}</p>
                <p className="text-sm text-on-surface-variant">{job.client}</p>
              </div>
              <span className="text-xs font-bold text-primary self-start">{job.status}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
