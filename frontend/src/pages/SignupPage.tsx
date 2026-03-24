import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
import type { PostSignupResponse } from '../types';
import {
  validateUsername,
  validateEmail,
  validatePassword,
  validateNameFirst,
  validateNameLast,
} from '../validation';

export function SignupPage() {
  const { signup } = useAuth();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [nameFirst, setNameFirst] = useState('');
  const [nameLast, setNameLast] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string | null>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [signupResult, setSignupResult] = useState<PostSignupResponse | null>(null);
  const [copyFeedback, setCopyFeedback] = useState<string | null>(null);

  function validate(): boolean {
    const e: Record<string, string | null> = {
      username: validateUsername(username),
      email: validateEmail(email),
      name_first: validateNameFirst(nameFirst),
      name_last: validateNameLast(nameLast),
      password: validatePassword(password),
      confirm_password: password !== confirmPassword ? 'Passwords do not match' : null,
    };
    setErrors(e);
    return !Object.values(e).some(Boolean);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setServerError(null);
    try {
      const result = await signup({
        username,
        email,
        name_first: nameFirst,
        name_last: nameLast,
        password,
      });
      setSignupResult(result);
    } catch (err) {
      const status = (err as { status?: number }).status;
      if (status === 429) {
        setServerError('Too many signup attempts. Please try again later.');
      } else {
        setServerError((err as Error).message);
      }
    } finally {
      setLoading(false);
    }
  }

  if (signupResult) {
    const debugToken = signupResult.metadata.verification_token;
    const verifyUrl = debugToken
      ? `/verify-email?token=${encodeURIComponent(debugToken)}`
      : '/verify-email';

    async function handleCopyToken() {
      if (!debugToken) return;

      try {
        await navigator.clipboard.writeText(debugToken);
        setCopyFeedback('Verification token copied.');
      } catch {
        setCopyFeedback('Unable to copy the verification token.');
      }
    }

    return (
      <div className="mx-auto max-w-xl pt-12">
        <h1 className="mb-4 text-2xl font-bold">Check your email</h1>
        <p className="mb-2 text-gray-600">
          Account creation succeeded for <span className="font-medium">{signupResult.email}</span>.
        </p>
        <p className="mb-6 text-sm text-gray-500">
          Verification expires at{' '}
          {new Date(signupResult.metadata.verification_expires_at).toLocaleString()}.
        </p>

        {debugToken ? (
          <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-medium text-amber-900">
              Debug verification mode is enabled on this server.
            </p>
            <p className="mt-1 text-sm text-amber-800">
              You can verify this account directly without waiting for email delivery.
            </p>
            <code className="mt-3 block overflow-x-auto rounded-md bg-white px-3 py-2 font-mono text-sm text-gray-800 ring-1 ring-amber-200">
              {debugToken}
            </code>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={handleCopyToken}
                className="rounded-md border border-amber-300 px-3 py-1.5 text-sm font-medium text-amber-900 hover:bg-amber-100"
              >
                Copy Token
              </button>
              <Link
                to={verifyUrl}
                className="rounded-md bg-amber-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-amber-700"
              >
                Verify Now
              </Link>
            </div>
            {copyFeedback && <p className="mt-2 text-sm text-amber-900">{copyFeedback}</p>}
          </div>
        ) : (
          <p className="mb-6 text-gray-600">
            We&apos;ve sent a verification link to your email address. Please verify your email
            before logging in.
          </p>
        )}

        <div className="flex flex-wrap gap-3">
          <Link to={verifyUrl} className="text-blue-600 hover:text-blue-800">
            Go to verification page
          </Link>
          <Link to="/login" className="text-blue-600 hover:text-blue-800">
            Go to login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-sm pt-12">
      <h1 className="mb-6 text-2xl font-bold">Sign up</h1>
      <form onSubmit={handleSubmit}>
        <FormField label="Username" error={errors.username}>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, username: validateUsername(username) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            autoFocus
          />
        </FormField>

        <FormField label="Email" error={errors.email}>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, email: validateEmail(email) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="First Name" error={errors.name_first}>
          <input
            value={nameFirst}
            onChange={(e) => setNameFirst(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, name_first: validateNameFirst(nameFirst) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Last Name" error={errors.name_last}>
          <input
            value={nameLast}
            onChange={(e) => setNameLast(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, name_last: validateNameLast(nameLast) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Password" error={errors.password}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => setErrors((p) => ({ ...p, password: validatePassword(password) }))}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        <FormField label="Confirm Password" error={errors.confirm_password}>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            onBlur={() =>
              setErrors((p) => ({
                ...p,
                confirm_password: password !== confirmPassword ? 'Passwords do not match' : null,
              }))
            }
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </FormField>

        {serverError && <p className="mb-4 text-sm text-red-600">{serverError}</p>}
        <SubmitButton loading={loading}>Sign up</SubmitButton>
      </form>
      <p className="mt-4 text-center text-sm text-gray-500">
        Already have an account?{' '}
        <Link to="/login" className="text-blue-600 hover:text-blue-800">
          Log in
        </Link>
      </p>
    </div>
  );
}
