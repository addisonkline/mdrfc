# mdrfc
A server for hosting Markdown-formatted RFCs

## Email Verification

`POST /signup` now creates an unverified account and sends an email verification link through SMTP.

Required environment variables for SMTP delivery:

- `APP_BASE_URL`
- `EMAIL_FROM`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

Optional environment variables:

- `SMTP_STARTTLS` (default `true`)
- `SMTP_USE_SSL` (default `false`)
- `EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES` (default `60`)
- `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN` (default `false`, for local development only)
