import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Send } from 'lucide-react';
import { ordersApi } from '@/api/endpoints';

export default function ReportPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [summary, setSummary] = useState('');
  const [labor, setLabor] = useState('');
  const [parts, setParts] = useState('');
  const [warranty, setWarranty] = useState('30');
  const [loading, setLoading] = useState(false);

  const total = (Number(labor) || 0) + (Number(parts) || 0);

  const submit = async () => {
    if (!id) return;
    setLoading(true);
    try {
      await ordersApi.submitReport(id, {
        summary,
        labor_cost: Number(labor) || 0,
        parts_cost: Number(parts) || 0,
        total,
        warranty_days: Number(warranty) || 30,
      });
      try {
        await ordersApi.updateStatus(id, 'completed');
      } catch {
        // Already completed or illegal transition — report still saved
      }
      navigate(`/orders/${id}`);
    } catch {
      alert(t('error_generic'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-full bg-surface pb-24">
      <header className="sticky top-0 z-20 pt-safe bg-surface-container-lowest/90 backdrop-blur-xl border-b border-outline-variant/20">
        <div className="h-14 px-3 flex items-center gap-2">
          <button
            onClick={() => navigate(-1)}
            className="w-10 h-10 rounded-full flex items-center justify-center hover:bg-surface-container"
          >
            <ArrowLeft size={22} />
          </button>
          <h1 className="font-semibold">{t('submit_report')}</h1>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm space-y-3">
          <label className="block text-xs font-semibold text-on-surface-variant uppercase">
            Technical Report
          </label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows={4}
            placeholder="Describe work performed, parts used, test results..."
            className="w-full rounded-xl bg-surface-container-low p-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
          />
        </div>

        <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm space-y-3">
          <h3 className="text-xs font-semibold text-on-surface-variant uppercase">Invoice</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-on-surface-variant">Labor (UZS)</label>
              <input
                type="number"
                value={labor}
                onChange={(e) => setLabor(e.target.value)}
                className="w-full h-11 mt-1 px-3 rounded-xl bg-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
            </div>
            <div>
              <label className="text-xs text-on-surface-variant">Parts (UZS)</label>
              <input
                type="number"
                value={parts}
                onChange={(e) => setParts(e.target.value)}
                className="w-full h-11 mt-1 px-3 rounded-xl bg-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-on-surface-variant">Warranty (days)</label>
            <input
              type="number"
              value={warranty}
              onChange={(e) => setWarranty(e.target.value)}
              className="w-full h-11 mt-1 px-3 rounded-xl bg-surface-container-low text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>
          <div className="flex justify-between items-center pt-2 border-t border-outline-variant/20">
            <span className="font-semibold">Total</span>
            <span className="text-lg font-bold text-primary">
              {total.toLocaleString()} UZS
            </span>
          </div>
        </div>
      </main>

      <div className="fixed bottom-0 inset-x-0 p-4 pb-safe bg-surface-container-lowest border-t border-outline-variant/20">
        <button
          onClick={submit}
          disabled={loading || !summary}
          className="w-full h-12 rounded-xl bg-primary text-on-primary font-semibold flex items-center justify-center gap-2 disabled:opacity-50 shadow-md"
        >
          <Send size={18} />
          {loading ? t('loading') : 'Submit & Complete'}
        </button>
      </div>
    </div>
  );
}
