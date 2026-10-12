import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { MapPin, ChevronRight, Search } from 'lucide-react';
import { ordersApi } from '@/api/endpoints';
import type { Order } from '@/types';
import StatusBadge from '@/components/StatusBadge';
import clsx from 'clsx';

const FILTERS = ['all', 'new', 'in_progress', 'completed'] as const;

function normalizeList(data: unknown): Order[] {
  if (Array.isArray(data)) return data;
  if (data && typeof data === 'object' && 'results' in data) {
    return (data as { results: Order[] }).results;
  }
  return [];
}

export default function OrdersPage() {
  const { t } = useTranslation();
  const [orders, setOrders] = useState<Order[]>([]);
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const params = filter === 'all' ? undefined : { status: filter };
        const { data } = await ordersApi.list(params);
        if (!cancelled) setOrders(normalizeList(data));
      } catch {
        if (!cancelled) {
          setOrders([]);
          setError(t('error_generic'));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [filter, t]);

  const filtered = orders.filter((o) => {
    if (!query) return true;
    const q = query.toLowerCase();
    return (
      o.number?.toLowerCase().includes(q) ||
      String(o.id).toLowerCase().includes(q) ||
      o.title?.toLowerCase().includes(q) ||
      o.client_name?.toLowerCase().includes(q) ||
      o.address?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="min-h-full bg-surface">
      <header className="sticky top-0 z-20 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="px-4 py-3 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-primary tracking-tight">{t('app_name')}</h1>
            <p className="text-[11px] font-medium text-on-surface-variant">Master Portal</p>
          </div>
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-surface-container text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
            {t('online')}
          </span>
        </div>

        <div className="px-4 pb-2">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-outline" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search orders..."
              className="w-full h-10 pl-9 pr-3 rounded-xl bg-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>
        </div>

        <div className="px-4 pb-3 flex gap-2 overflow-x-auto no-scrollbar">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={clsx(
                'px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-colors',
                filter === f
                  ? 'bg-primary text-on-primary shadow-sm'
                  : 'bg-surface-container text-on-surface-variant hover:bg-surface-container-high'
              )}
            >
              {t(f)}
            </button>
          ))}
        </div>
      </header>

      <main className="px-4 py-4 space-y-3">
        {loading && (
          <div className="text-center py-12 text-on-surface-variant text-sm">{t('loading')}</div>
        )}

        {!loading && error && (
          <div className="text-center py-12 text-error text-sm bg-error-container/40 rounded-2xl px-4">
            {error}
          </div>
        )}

        {!loading && !error && filtered.length === 0 && (
          <div className="text-center py-16 text-on-surface-variant">
            <p className="font-medium">{t('no_orders')}</p>
          </div>
        )}

        {filtered.map((order) => (
          <Link
            key={order.id}
            to={`/orders/${order.id}`}
            className="block bg-surface-container-lowest rounded-2xl p-4 shadow-sm border border-outline-variant/15 active:scale-[0.99] transition-transform"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-bold text-on-surface-variant">
                    #{order.number || order.id}
                  </span>
                  <StatusBadge status={order.status} />
                </div>
                <h3 className="font-semibold text-on-surface mt-1 truncate">{order.title}</h3>
              </div>
              {order.price != null && (
                <span className="text-sm font-bold text-primary shrink-0">
                  {Number(order.price).toLocaleString()} UZS
                </span>
              )}
            </div>

            <p className="text-sm text-on-surface-variant truncate mb-2">
              {order.client_name}
            </p>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1 text-xs text-on-surface-variant min-w-0">
                <MapPin size={14} className="shrink-0 text-outline" />
                <span className="truncate">{order.address}</span>
              </div>
              <ChevronRight size={18} className="text-outline shrink-0" />
            </div>
          </Link>
        ))}
      </main>
    </div>
  );
}
