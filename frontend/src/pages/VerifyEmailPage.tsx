import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { verifyEmail } from '../api/auth';

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('No verification token provided.');
      return;
    }
    verifyEmail(token)
      .then((res) => {
        setStatus('success');
        setMessage(`Email verified for ${res.username}. You can now log in.`);
      })
      .catch((err) => {
        setStatus('error');
        setMessage(err.message || 'Verification failed.');
      });
  }, [token]);

  return (
    <div className="mx-auto max-w-sm pt-12 text-center">
      <h1 className="mb-4 text-2xl font-bold">Email Verification</h1>
      {status === 'loading' && <p className="text-gray-500">Verifying...</p>}
      {status === 'success' && (
        <>
          <p className="mb-4 text-green-600">{message}</p>
          <Link to="/login" className="text-blue-600 hover:text-blue-800">
            Go to login
          </Link>
        </>
      )}
      {status === 'error' && <p className="text-red-600">{message}</p>}
    </div>
  );
}
