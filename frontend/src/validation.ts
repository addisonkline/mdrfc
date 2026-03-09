const USERNAME_RE = /^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

export function validateUsername(value: string): string | null {
  if (value.length < 3) return 'Username must be at least 3 characters';
  if (value.length > 16) return 'Username must be 16 characters or less';
  if (!USERNAME_RE.test(value.toLowerCase()))
    return 'Username must contain only lowercase letters, digits, \'.\', \'_\' or \'-\'';
  return null;
}

export function validateEmail(value: string): string | null {
  if (value.length > 64) return 'Email must be 64 characters or less';
  if (!EMAIL_RE.test(value.toLowerCase())) return 'Must be a valid email address';
  return null;
}

export function validatePassword(value: string): string | null {
  if (value.length < 12) return 'Password must be at least 12 characters';
  if (value.length > 128) return 'Password must be 128 characters or less';
  if (value.trim().length === 0) return 'Password must not be whitespace only';
  return null;
}

export function validateNameFirst(value: string): string | null {
  if (value.trim().length === 0) return 'First name must not be empty';
  if (value.length > 32) return 'First name must be 32 characters or less';
  return null;
}

export function validateNameLast(value: string): string | null {
  if (value.trim().length === 0) return 'Last name must not be empty';
  if (value.length > 32) return 'Last name must be 32 characters or less';
  return null;
}

export function validateRfcTitle(value: string): string | null {
  if (value.trim().length === 0) return 'Title is required';
  if (value.length > 64) return 'Title must be 64 characters or less';
  return null;
}

export function validateRfcSlug(value: string): string | null {
  if (value.trim().length === 0) return 'Slug is required';
  if (value.length > 32) return 'Slug must be 32 characters or less';
  return null;
}

export function validateRfcSummary(value: string): string | null {
  if (value.trim().length === 0) return 'Summary is required';
  if (value.length > 256) return 'Summary must be 256 characters or less';
  return null;
}

export function validateRfcContent(value: string): string | null {
  if (value.trim().length === 0) return 'Content is required';
  if (value.length > 65536) return 'Content must be 65,536 characters or less';
  return null;
}

export function validateCommentContent(value: string): string | null {
  if (value.trim().length === 0) return 'Comment must not be empty';
  if (value.length > 4096) return 'Comment must be 4,096 characters or less';
  return null;
}
