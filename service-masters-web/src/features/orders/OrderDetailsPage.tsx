import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  ArrowLeft,
  MapPin,
  Phone,
  Camera,
  FileText,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import { ordersApi } from '@/api/endpoints';
import type { Order, OrderStatus } from '@/types';
import StatusBadge from '@/components/StatusBadge';

const STEPS: { key: OrderStatus; label: string }[] = [
  { key: 'accepted', label: 'Accepted' },
  { key: 'en_route', label: 'En Route' },
  { key: 'on_site', label: 'On Site' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'completed', label: 'Completed' },
];

/** Next legal status for master workflow buttons */
const NEXT_STATUS: Partial<Record<OrderStatus, { status: OrderStatus; label: string }>> = {
  new: { status: 'accepted', label: 'Accept Order' },
  accepted: { status: 'en_route', label: 'Start En Route' },
  en_route: { status: 'on_site', label: 'Arrived On Site' },
  on_site: { status: 'in_progress', label: 'Start Work' },
  in_progress: { status: 'completed', label: 'Mark Completed' },
};

function mediaUrl(path: string) {
  if (!path) return path;
  if (path.startsWith('http')) return path;
  const api = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const origin = api.replace(/\/api\/?$/, '');
  return `${origin}${path.startsWith('/') ? path : `/${path}`}`;
}

export default function OrderDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      setError('');
      try {
        const { data } = await ordersApi.get(id);
        if (!cancelled) setOrder(data);
      } catch {
        if (!cancelled) {
          setOrder(null);
          setError(t('error_generic'));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [id, t]);

  const updateStatus = async (status: string) => {
    if (!id) return;
    setUpdating(true);
    try {
      const { data } = await ordersApi.updateStatus(id, status);
      setOrder(data);
    } catch {
      alert(t('error_generic'));
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-full flex items-center justify-center text-on-surface-variant">
        {t('loading')}
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-full flex flex-col items-center justify-center gap-3 px-4">
        <p className="text-on-surface-variant">{error || 'Order not found'}</p>
        <button onClick={() => navigate('/orders')} className="text-primary font-semibold">
          Go back
        </button>
      </div>
    );
  }

  const stepIndex =
    order.status === 'new'
      ? -1
      : STEPS.findIndex((s) => s.key === order.status);
  const nextAction = NEXT_STATUS[order.status];

  return (
    <div className="min-h-full bg-surface pb-36">
      <header className="sticky top-0 z-20 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="h-14 px-3 flex items-center gap-2">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-full flex items-center justify-center hover:bg-surface-container"
          >
            <ArrowLeft size={22} />
          </button>
          <div className="min-w-0 flex-1">
            <h1 className="font-semibold text-on-surface truncate">
              #{order.number || order.id}
            </h1>
            <StatusBadge status={order.status} />
          </div>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
          <h2 className="text-lg font-bold text-on-surface">{order.title}</h2>
          {order.description && (
            <p className="text-sm text-on-surface-variant mt-1">{order.description}</p>
          )}
          {order.price != null && (
            <p className="text-xl font-bold text-primary mt-3">
              {Number(order.price).toLocaleString()} UZS
            </p>
          )}
        </div>

        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm space-y-3">
          <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider">
            Client
          </h3>
          <div className="flex items-center justify-between">
            <span className="font-semibold text-on-surface">{order.client_name}</span>
            {order.client_phone && (
              <a
                href={`tel:${order.client_phone}`}
                className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center"
              >
                <Phone size={18} />
              </a>
            )}
          </div>
          <div className="flex items-start gap-2 text-sm text-on-surface-variant">
            <MapPin size={16} className="mt-0.5 shrink-0" />
            <span>{order.address}</span>
          </div>
        </div>

        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-4">
            Progress
          </h3>
          <div className="space-y-0">
            {STEPS.map((step, i) => {
              const done = stepIndex >= i;
              const active = stepIndex === i;
              return (
                <div key={step.key} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 ${
                        done
                          ? 'bg-primary text-on-primary'
                          : 'bg-surface-container text-outline'
                      }`}
                    >
                      {done ? <CheckCircle2 size={16} /> : <Clock size={14} />}
                    </div>
                    {i < STEPS.length - 1 && (
                      <div
                        className={`w-0.5 h-8 ${done ? 'bg-primary' : 'bg-surface-container-high'}`}
                      />
                    )}
                  </div>
                  <div className={`pt-1 pb-4 ${active ? 'text-primary font-semibold' : ''}`}>
                    {step.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {order.photos && order.photos.length > 0 && (
          <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider mb-3">
              Photos
            </h3>
            <div className="grid grid-cols-3 gap-2">
              {order.photos.map((p) => (
                <div key={p.id} className="aspect-square rounded-xl overflow-hidden bg-surface-container">
                  <img
                    src={mediaUrl(p.image)}
                    alt={p.kind}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {order.report && (
          <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm space-y-2">
            <h3 className="text-sm font-semibold text-on-surface-variant uppercase tracking-wider">
              Report
            </h3>
            <p className="text-sm text-on-surface">{order.report.summary}</p>
            <p className="text-sm font-semibold text-primary">
              {Number(order.report.total).toLocaleString()} UZS · {order.report.warranty_days}d warranty
            </p>
          </div>
        )}
      </main>

      <div className="fixed bottom-0 inset-x-0 z-30 px-4 pb-safe pt-2 bg-gradient-to-t from-surface via-surface to-transparent">
        <div className="max-w-lg mx-auto space-y-2 pb-3">
          <div className="flex gap-2">
            <Link
              to={`/orders/${order.id}/photos`}
              className="flex-1 h-12 rounded-xl bg-surface-container-high text-on-surface font-semibold flex items-center justify-center gap-2"
            >
              <Camera size={18} />
              {t('upload_photos')}
            </Link>
            <Link
              to={`/orders/${order.id}/report`}
              className="flex-1 h-12 rounded-xl bg-primary text-on-primary font-semibold flex items-center justify-center gap-2 shadow-md"
            >
              <FileText size={18} />
              {t('submit_report')}
            </Link>
          </div>
          {nextAction && order.status !== 'completed' && order.status !== 'cancelled' && (
            <button
              onClick={() => updateStatus(nextAction.status)}
              disabled={updating}
              className="w-full h-11 rounded-xl bg-secondary text-on-secondary font-semibold disabled:opacity-60"
            >
              {updating ? t('loading') : nextAction.label}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
