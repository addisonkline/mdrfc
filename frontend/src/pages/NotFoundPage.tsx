import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="py-20 text-center">
      <h1 className="mb-2 text-4xl font-bold text-gray-900">404</h1>
      <p className="mb-6 text-gray-500">Page not found</p>
      <Link to="/" className="text-blue-600 hover:text-blue-800">
        Back to home
      </Link>
    </div>
  );
}
