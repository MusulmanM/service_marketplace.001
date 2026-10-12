import { Outlet } from 'react-router-dom';
import BottomNav from './BottomNav';

export default function AppShell() {
  return (
    <div className="min-h-full flex flex-col bg-surface">
      <div className="flex-1 pb-20">
        <Outlet />
      </div>
      <BottomNav />
    </div>
  );
}
