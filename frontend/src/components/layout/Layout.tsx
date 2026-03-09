import { Outlet } from 'react-router-dom';
import { Header } from './Header';
import { Footer } from './Footer';

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 text-gray-900">
      <Header />
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
