import clsx from 'clsx';
import type { OrderStatus } from '@/types';

const MAP: Record<string, { label: string; className: string }> = {
  new: { label: 'New', className: 'bg-primary/10 text-primary' },
  accepted: { label: 'Accepted', className: 'bg-secondary-container text-on-secondary-container' },
  en_route: { label: 'En Route', className: 'bg-tertiary/15 text-tertiary' },
  on_site: { label: 'On Site', className: 'bg-primary-container text-on-primary-container' },
  in_progress: { label: 'In Progress', className: 'bg-primary-container text-on-primary' },
  completed: { label: 'Completed', className: 'bg-secondary/15 text-secondary' },
  cancelled: { label: 'Cancelled', className: 'bg-error-container text-error' },
  rejected: { label: 'Rejected', className: 'bg-error-container text-error' },
  pending_review: { label: 'Pending Review', className: 'bg-surface-container-high text-on-surface-variant' },
};

export default function StatusBadge({ status }: { status: OrderStatus | string }) {
  const cfg = MAP[status] || { label: status, className: 'bg-surface-container text-on-surface-variant' };
  return (
    <span className={clsx('inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold', cfg.className)}>
      {cfg.label}
    </span>
  );
}
