const USERNAME_RE = /^[a-z0-9][a-z0-9._-]*[a-z0-9]$|^[a-z0-9]$/;
const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

const LEN_USERNAME_MIN = 3;
const LEN_USERNAME_MAX = 16;
const LEN_EMAIL_MIN = 3;
const LEN_EMAIL_MAX = 64;
const LEN_PASSWORD_MIN = 12;
const LEN_PASSWORD_MAX = 128;
const LEN_NAME_MIN = 3;
const LEN_NAME_MAX = 32;
const LEN_RFC_TITLE_MIN = 8;
const LEN_RFC_TITLE_MAX = 64;
const LEN_RFC_SLUG_MIN = 4;
const LEN_RFC_SLUG_MAX = 32;
const LEN_RFC_SUMMARY_MIN = 8;
const LEN_RFC_SUMMARY_MAX = 256;
const LEN_RFC_CONTENT_MIN = 8;
const LEN_RFC_CONTENT_MAX = 65536;
const LEN_COMMENT_CONTENT_MIN = 4;
const LEN_COMMENT_CONTENT_MAX = 4096;
const LEN_REVISION_MESSAGE_MIN = 4;
const LEN_REVISION_MESSAGE_MAX = 256;
const LEN_QUARANTINE_RFC_REASON_MIN = 8;
const LEN_QUARANTINE_RFC_REASON_MAX = 2048;
const LEN_QUARANTINE_COMMENT_REASON_MIN = 8;
const LEN_QUARANTINE_COMMENT_REASON_MAX = 1024;
const LEN_README_REASON_MIN = 8;
const LEN_README_REASON_MAX = 2048;
const LEN_README_CONTENT_MIN = 8;
const LEN_README_CONTENT_MAX = 65536;
const LEN_RFC_REVIEW_REASON_MIN = 8;
const LEN_RFC_REVIEW_REASON_MAX = 2048;
const LEN_VERIFICATION_TOKEN_MIN = 32;
const LEN_AGENT_NAME_MIN = 1;
const LEN_AGENT_NAME_MAX = 32;
const LEN_HOST_NAME_MIN = 1;
const LEN_HOST_NAME_MAX = 32;

export function validateUsername(value: string): string | null {
  if (value.length < LEN_USERNAME_MIN) {
    return `Username must be at least ${LEN_USERNAME_MIN} characters`;
  }
  if (value.length > LEN_USERNAME_MAX) {
    return `Username must be ${LEN_USERNAME_MAX} characters or less`;
  }
  if (!USERNAME_RE.test(value.toLowerCase())) {
    return "Username must contain only lowercase letters, digits, '.', '_' or '-'";
  }
  return null;
}

export function validateEmail(value: string): string | null {
  if (value.length < LEN_EMAIL_MIN) {
    return `Email must be at least ${LEN_EMAIL_MIN} characters`;
  }
  if (value.length > LEN_EMAIL_MAX) {
    return `Email must be ${LEN_EMAIL_MAX} characters or less`;
  }
  if (!EMAIL_RE.test(value.toLowerCase())) {
    return 'Must be a valid email address';
  }
  return null;
}

export function validatePassword(value: string): string | null {
  if (value.length < LEN_PASSWORD_MIN) {
    return `Password must be at least ${LEN_PASSWORD_MIN} characters`;
  }
  if (value.length > LEN_PASSWORD_MAX) {
    return `Password must be ${LEN_PASSWORD_MAX} characters or less`;
  }
  if (value.trim().length === 0) {
    return 'Password must not be whitespace only';
  }
  return null;
}

export function validateNameFirst(value: string): string | null {
  if (value.length < LEN_NAME_MIN) {
    return `First name must be at least ${LEN_NAME_MIN} characters`;
  }
  if (value.length > LEN_NAME_MAX) {
    return `First name must be ${LEN_NAME_MAX} characters or less`;
  }
  return null;
}

export function validateNameLast(value: string): string | null {
  if (value.length < LEN_NAME_MIN) {
    return `Last name must be at least ${LEN_NAME_MIN} characters`;
  }
  if (value.length > LEN_NAME_MAX) {
    return `Last name must be ${LEN_NAME_MAX} characters or less`;
  }
  return null;
}

export function validateRfcTitle(value: string): string | null {
  if (value.length < LEN_RFC_TITLE_MIN) {
    return `Title must be at least ${LEN_RFC_TITLE_MIN} characters`;
  }
  if (value.length > LEN_RFC_TITLE_MAX) {
    return `Title must be ${LEN_RFC_TITLE_MAX} characters or less`;
  }
  return null;
}

export function validateRfcSlug(value: string): string | null {
  if (value.length < LEN_RFC_SLUG_MIN) {
    return `Slug must be at least ${LEN_RFC_SLUG_MIN} characters`;
  }
  if (value.length > LEN_RFC_SLUG_MAX) {
    return `Slug must be ${LEN_RFC_SLUG_MAX} characters or less`;
  }
  return null;
}

export function validateRfcSummary(value: string): string | null {
  if (value.length < LEN_RFC_SUMMARY_MIN) {
    return `Summary must be at least ${LEN_RFC_SUMMARY_MIN} characters`;
  }
  if (value.length > LEN_RFC_SUMMARY_MAX) {
    return `Summary must be ${LEN_RFC_SUMMARY_MAX} characters or less`;
  }
  return null;
}

export function validateRfcContent(value: string): string | null {
  if (value.length < LEN_RFC_CONTENT_MIN) {
    return `Content must be at least ${LEN_RFC_CONTENT_MIN} characters`;
  }
  if (value.length > LEN_RFC_CONTENT_MAX) {
    return `Content must be ${LEN_RFC_CONTENT_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateCommentContent(value: string): string | null {
  if (value.length < LEN_COMMENT_CONTENT_MIN) {
    return `Comment must be at least ${LEN_COMMENT_CONTENT_MIN} characters`;
  }
  if (value.length > LEN_COMMENT_CONTENT_MAX) {
    return `Comment must be ${LEN_COMMENT_CONTENT_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateRevisionMessage(value: string): string | null {
  if (value.length < LEN_REVISION_MESSAGE_MIN) {
    return `Revision message must be at least ${LEN_REVISION_MESSAGE_MIN} characters`;
  }
  if (value.length > LEN_REVISION_MESSAGE_MAX) {
    return `Revision message must be ${LEN_REVISION_MESSAGE_MAX} characters or less`;
  }
  return null;
}

export function validateQuarantineRfcReason(value: string): string | null {
  if (value.length < LEN_QUARANTINE_RFC_REASON_MIN) {
    return `Reason must be at least ${LEN_QUARANTINE_RFC_REASON_MIN} characters`;
  }
  if (value.length > LEN_QUARANTINE_RFC_REASON_MAX) {
    return `Reason must be ${LEN_QUARANTINE_RFC_REASON_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateQuarantineCommentReason(value: string): string | null {
  if (value.length < LEN_QUARANTINE_COMMENT_REASON_MIN) {
    return `Reason must be at least ${LEN_QUARANTINE_COMMENT_REASON_MIN} characters`;
  }
  if (value.length > LEN_QUARANTINE_COMMENT_REASON_MAX) {
    return `Reason must be ${LEN_QUARANTINE_COMMENT_REASON_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateReadmeReason(value: string): string | null {
  if (value.length < LEN_README_REASON_MIN) {
    return `Reason must be at least ${LEN_README_REASON_MIN} characters`;
  }
  if (value.length > LEN_README_REASON_MAX) {
    return `Reason must be ${LEN_README_REASON_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateReadmeContent(value: string): string | null {
  if (value.length < LEN_README_CONTENT_MIN) {
    return `Content must be at least ${LEN_README_CONTENT_MIN} characters`;
  }
  if (value.length > LEN_README_CONTENT_MAX) {
    return `Content must be ${LEN_README_CONTENT_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateRfcReviewReason(value: string): string | null {
  if (value.length < LEN_RFC_REVIEW_REASON_MIN) {
    return `Reason must be at least ${LEN_RFC_REVIEW_REASON_MIN} characters`;
  }
  if (value.length > LEN_RFC_REVIEW_REASON_MAX) {
    return `Reason must be ${LEN_RFC_REVIEW_REASON_MAX.toLocaleString()} characters or less`;
  }
  return null;
}

export function validateVerificationToken(value: string): string | null {
  if (value.trim().length < LEN_VERIFICATION_TOKEN_MIN) {
    return `Verification token must be at least ${LEN_VERIFICATION_TOKEN_MIN} characters`;
  }
  return null;
}

export function parseAgentContributors(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((entry) => entry.trim())
    .filter(Boolean);
}

function validateAgentContributor(value: string): string | null {
  if (!value.includes('@')) {
    return "Agent contributors must use the format 'agent@host'";
  }

  const [agent, host] = value.split('@', 2);
  if (agent.length < LEN_AGENT_NAME_MIN || agent.length > LEN_AGENT_NAME_MAX) {
    return `Agent names must be between ${LEN_AGENT_NAME_MIN} and ${LEN_AGENT_NAME_MAX} characters`;
  }
  if (host.length < LEN_HOST_NAME_MIN || host.length > LEN_HOST_NAME_MAX) {
    return `Host names must be between ${LEN_HOST_NAME_MIN} and ${LEN_HOST_NAME_MAX} characters`;
  }

  return null;
}

export function validateAgentContributors(value: string): string | null {
  for (const contributor of parseAgentContributors(value)) {
    const error = validateAgentContributor(contributor);
    if (error) {
      return error;
    }
  }
  return null;
}

export function formatAgentContributors(contributors: string[]): string {
  return contributors.join('\n');
}
