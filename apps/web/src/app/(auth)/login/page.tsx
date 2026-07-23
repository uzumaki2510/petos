import { LoginForm } from '@/components/auth/login-form';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In | PetOS',
  description: 'Sign in to your PetOS workspace.',
};

export default function LoginPage() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50/50 dark:bg-gray-900/50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
            PetOS
          </h1>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
