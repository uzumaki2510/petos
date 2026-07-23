import { Metadata } from 'next';
import { getCurrentUser } from '@/lib/api/server';

export const metadata: Metadata = {
  title: 'Settings | PetOS',
};

export default async function SettingsPage() {
  const user = await getCurrentUser();

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-2">Manage your account settings.</p>
      </div>

      <div className="rounded-lg border p-6 space-y-4">
        <h2 className="text-xl font-semibold">Profile</h2>
        <div className="grid gap-2">
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-sm font-medium text-muted-foreground">Display Name</span>
            <span className="text-sm">{user?.display_name}</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-sm font-medium text-muted-foreground">Email</span>
            <span className="text-sm">{user?.email}</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-sm font-medium text-muted-foreground">Account Status</span>
            <span className="text-sm capitalize">{user?.status}</span>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-destructive/30 p-6 space-y-4 bg-red-50/50 dark:bg-red-900/10">
        <h2 className="text-xl font-semibold text-red-700 dark:text-red-400">Danger Zone</h2>
        <p className="text-sm text-muted-foreground">
          Account deletion and workspace management features are coming in a future phase.
        </p>
      </div>
    </div>
  );
}
