import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { verifyEmail } from '../api/auth';
import { validateVerificationToken } from '../validation';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const tokenFromQuery = searchParams.get('token') ?? '';
  const [token, setToken] = useState(tokenFromQuery);
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>(
    tokenFromQuery ? 'loading' : 'idle',
  );
  const [message, setMessage] = useState<string | null>(null);

  async function runVerification(nextToken: string) {
    const validationError = validateVerificationToken(nextToken);
    if (validationError) {
      setStatus('error');
      setMessage(validationError);
      return;
    }

    setStatus('loading');
    setMessage(null);

    try {
      const response = await verifyEmail(nextToken);
      setStatus('success');
      setMessage(`Email verified for ${response.username}. You can now log in.`);
    } catch (err) {
      setStatus('error');
      setMessage((err as Error).message || 'Verification failed.');
    }
  }

  useEffect(() => {
    if (!tokenFromQuery) {
      return;
    }

    verifyEmail(tokenFromQuery)
      .then((response) => {
        setStatus('success');
        setMessage(`Email verified for ${response.username}. You can now log in.`);
      })
      .catch((err) => {
        setStatus('error');
        setMessage((err as Error).message || 'Verification failed.');
      });
  }, [tokenFromQuery]);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await runVerification(token);
  }

  return (
    <div className="mx-auto max-w-md pt-12">
      <h1 className="mb-4 text-2xl font-bold">Email Verification</h1>
      <p className="mb-6 text-sm text-gray-500">
        Paste a verification token manually, or open this page from the emailed verification link.
      </p>

      {status === 'loading' && <p className="mb-4 text-gray-500">Verifying...</p>}
      {status === 'success' && (
        <>
          <p className="mb-4 text-green-600">{message}</p>
          <Link to="/login" className="text-blue-600 hover:text-blue-800">
            Go to login
          </Link>
        </>
      )}

      {status !== 'success' && (
        <form onSubmit={handleSubmit}>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Verification Token
          </label>
          <textarea
            value={token}
            onChange={(event) => setToken(event.target.value)}
            rows={3}
            className="w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm focus:border-blue-500 focus:outline-none"
          />
          {status === 'error' && message && <p className="mt-2 text-sm text-red-600">{message}</p>}
          <button
            type="submit"
            disabled={status === 'loading'}
            className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {status === 'loading' ? 'Verifying...' : 'Verify Email'}
          </button>
        </form>
      )}
    </div>
  );
}
