import { NavLink } from 'react-router-dom';

const LINKS = [
  { to: '/admin/review-needed', label: 'Review Queue' },
  { to: '/admin/quarantined/rfcs', label: 'Quarantined RFCs' },
];

export function AdminNav() {
  return (
    <nav className="mb-6 flex flex-wrap gap-2">
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            `rounded-md px-3 py-1.5 text-sm font-medium ${
              isActive
                ? 'bg-gray-900 text-white'
                : 'bg-white text-gray-600 ring-1 ring-gray-200 hover:bg-gray-50'
            }`
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
