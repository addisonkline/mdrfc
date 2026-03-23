import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <div className="mx-auto max-w-sm pt-12">
      <h1 className="mb-6 text-2xl font-bold">Profile</h1>
      <dl className="space-y-3 text-sm">
        <div>
          <dt className="font-medium text-gray-500">Username</dt>
          <dd className="text-gray-900">{user.username}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-500">Email</dt>
          <dd className="text-gray-900">{user.email}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-500">Name</dt>
          <dd className="text-gray-900">
            {user.name_first} {user.name_last}
          </dd>
        </div>
        <div>
          <dt className="font-medium text-gray-500">Joined</dt>
          <dd className="text-gray-900">{new Date(user.created_at).toLocaleDateString()}</dd>
        </div>
        <div>
          <dt className="font-medium text-gray-500">Role</dt>
          <dd className="text-gray-900">{user.is_admin ? 'Admin' : 'User'}</dd>
        </div>
      </dl>
      <button
        onClick={handleLogout}
        className="mt-8 w-full rounded-md border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
      >
        Log out
      </button>
    </div>
  );
}
