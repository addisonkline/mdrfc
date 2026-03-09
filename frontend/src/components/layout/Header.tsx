import { Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export function Header() {
  const { isAuthenticated, user } = useAuth();

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link to="/" className="text-xl font-bold text-gray-900">
          mdrfc
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/" className="text-gray-600 hover:text-gray-900">
            RFCs
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/rfc/new" className="text-gray-600 hover:text-gray-900">
                New RFC
              </Link>
              <Link to="/profile" className="text-gray-600 hover:text-gray-900">
                {user?.username}
              </Link>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-600 hover:text-gray-900">
                Log in
              </Link>
              <Link
                to="/signup"
                className="rounded-md bg-blue-600 px-3 py-1.5 text-white hover:bg-blue-700"
              >
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
