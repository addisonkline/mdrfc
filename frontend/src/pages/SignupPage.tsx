import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FormField } from '../components/forms/FormField';
import { SubmitButton } from '../components/forms/SubmitButton';
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
  const [success, setSuccess] = useState(false);

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
      await signup({
        username,
        email,
        name_first: nameFirst,
        name_last: nameLast,
        password,
      });
      setSuccess(true);
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

  if (success) {
    return (
      <div className="mx-auto max-w-sm pt-12 text-center">
        <h1 className="mb-4 text-2xl font-bold">Check your email</h1>
        <p className="mb-4 text-gray-600">
          We've sent a verification link to your email address. Please verify your email before
          logging in.
        </p>
        <Link to="/login" className="text-blue-600 hover:text-blue-800">
          Go to login
        </Link>
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
