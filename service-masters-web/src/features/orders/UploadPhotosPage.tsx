import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ArrowLeft, Camera, ImagePlus } from 'lucide-react';
import { ordersApi } from '@/api/endpoints';

export default function UploadPhotosPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [before, setBefore] = useState<File[]>([]);
  const [after, setAfter] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);

  const onPick = (
    e: React.ChangeEvent<HTMLInputElement>,
    setter: React.Dispatch<React.SetStateAction<File[]>>
  ) => {
    const files = Array.from(e.target.files || []);
    setter((prev) => [...prev, ...files]);
  };

  const upload = async () => {
    if (!id) return;
    setUploading(true);
    try {
      for (const file of before) {
        const fd = new FormData();
        fd.append('image', file);
        fd.append('kind', 'before');
        await ordersApi.uploadPhoto(id, fd);
      }
      for (const file of after) {
        const fd = new FormData();
        fd.append('image', file);
        fd.append('kind', 'after');
        await ordersApi.uploadPhoto(id, fd);
      }
      navigate(`/orders/${id}`);
    } catch {
      alert(t('error_generic'));
    } finally {
      setUploading(false);
    }
  };

  const Zone = ({
    title,
    files,
    onChange,
  }: {
    title: string;
    files: File[];
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  }) => (
    <div className="bg-surface-container-lowest rounded-2xl p-4 shadow-sm">
      <h3 className="font-semibold text-on-surface mb-3">{title}</h3>
      <label className="flex flex-col items-center justify-center gap-2 h-36 rounded-xl border-2 border-dashed border-outline-variant bg-surface-container-low cursor-pointer hover:bg-surface-container transition-colors">
        <ImagePlus className="text-primary" size={28} />
        <span className="text-sm text-on-surface-variant">Tap to add photos</span>
        <input type="file" accept="image/*" multiple className="hidden" onChange={onChange} />
      </label>
      {files.length > 0 && (
        <div className="grid grid-cols-3 gap-2 mt-3">
          {files.map((f, i) => (
            <div key={i} className="aspect-square rounded-lg overflow-hidden bg-surface-container">
              <img src={URL.createObjectURL(f)} alt="" className="w-full h-full object-cover" />
            </div>
          ))}
        </div>
      )}
    </div>
  );

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
          <h1 className="font-semibold">{t('upload_photos')}</h1>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        <Zone title="Before" files={before} onChange={(e) => onPick(e, setBefore)} />
        <Zone title="After" files={after} onChange={(e) => onPick(e, setAfter)} />
      </main>

      <div className="fixed bottom-0 inset-x-0 p-4 pb-safe bg-surface-container-lowest border-t border-outline-variant/20">
        <button
          onClick={upload}
          disabled={uploading || (before.length === 0 && after.length === 0)}
          className="w-full h-12 rounded-xl bg-primary text-on-primary font-semibold flex items-center justify-center gap-2 disabled:opacity-50 shadow-md"
        >
          <Camera size={18} />
          {uploading ? t('loading') : 'Upload Photos'}
        </button>
      </div>
    </div>
  );
}
