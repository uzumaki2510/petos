import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { LoginForm } from '../src/components/auth/login-form';
import { RegisterForm } from '../src/components/auth/register-form';

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    refresh: vi.fn(),
  }),
}));

test('Login form renders correctly', () => {
  render(<LoginForm />);
  expect(screen.getByText('Welcome back')).toBeDefined();
  expect(screen.getByLabelText('Email')).toBeDefined();
  expect(screen.getByLabelText('Password')).toBeDefined();
  expect(screen.getByRole('button', { name: 'Sign in' })).toBeDefined();
});

test('Register form renders correctly', () => {
  render(<RegisterForm />);
  expect(screen.getByText('Create an account')).toBeDefined();
  expect(screen.getByLabelText('Full Name')).toBeDefined();
  expect(screen.getByLabelText('Email')).toBeDefined();
  expect(screen.getByLabelText('Password')).toBeDefined();
  expect(screen.getByRole('button', { name: 'Create account' })).toBeDefined();
});
