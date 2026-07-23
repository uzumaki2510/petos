import { getCurrentUser } from '@/lib/api/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  if (!user) {
    redirect('/login');
  }

  return (
    <div className="flex min-h-screen flex-col bg-gray-50/50 dark:bg-gray-900/50">
      <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-white dark:bg-gray-950 px-6">
        <Link href="/app" className="flex items-center gap-2 font-semibold">
          <span>PetOS</span>
        </Link>
        <nav className="flex items-center gap-4 text-sm ml-6">
          <Link href="/app" className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50">
            Home
          </Link>
          <Link href="/app/projects" className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50">
            Projects
          </Link>
          <Link href="/app/settings" className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-50">
            Settings
          </Link>
        </nav>
        <div className="ml-auto flex items-center gap-4 text-sm">
          <span>{user.display_name}</span>
          <form action={async () => {
            'use server';
            const { logoutAction } = await import('@/app/actions/auth');
            await logoutAction();
            redirect('/login');
          }}>
            <button id="logout-button" type="submit" className="text-gray-500 hover:text-gray-900 dark:hover:text-gray-50">
              Logout
            </button>
          </form>
        </div>
      </header>
      <main className="flex-1 p-6">
        {children}
      </main>
    </div>
  );
}
