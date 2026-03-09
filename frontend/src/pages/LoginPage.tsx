import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const redirect = searchParams.get('redirect') || '/';

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(username, password);
      navigate(redirect);
    } catch (err) {
      const status = (err as { status?: number }).status;
      if (status === 401) {
        setError('Incorrect username or password');
      } else if (status === 403) {
        setError('Please verify your email first');
      } else {
        setError((err as Error).message);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm pt-12">
      <h1 className="mb-6 text-2xl font-bold">Log in</h1>
      <form onSubmit={handleSubmit}>
        <FormField label="Username">
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            autoFocus
          />
        </FormField>

        <FormField label="Password">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
        <SubmitButton loading={loading}>Log in</SubmitButton>
      </form>
      <p className="mt-4 text-center text-sm text-gray-500">
        Don't have an account?{' '}
        <Link to="/signup" className="text-blue-600 hover:text-blue-800">
          Sign up
        </Link>
      </p>
    </div>
  );
}
