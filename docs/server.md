# MDRFC Server Documentation

This document contains instructions for setting up the MDRFC server, SMTP integration, and configuration.

## Basic Setup

First, follow [quickstart.md](/docs/quickstart.md) for instructions on downloading/installing MDRFC and setting the necessary environment variables.

The database needs to be properly (i.e., all tables created with their required columns). With the virtual environment activated, run the following:

```bash
alembic upgrade head
```

Next, with your server running, try creating a new user:

```bash
curl -X POST http://localhost:8026/signup \
-H "Content-Type: application/json" \
-d '{"username":"test","email":"test@example.com","name_last":"User","name_first":"Test","password":"insecurechangeme"}'
```

If everything is set up correctly, you should get a `200` response containing, among other things, a `verification_token` string in the `metadata`.

Use this to verify your new account on the server:

```bash
curl -X POST http://localhost:8026/verify-email \
-H "Content-Type: application/json" \
-d '{"token":"{your_verification_token}"}'
```

You should get a `200` response indicating your account was successfully verified.

Now try connecting to the server with the client:

```bash
mdrfc client http://localhost:8026 --no-login
```

You should enter the CLI client REPL, but without being logged in. Try logging in with your credentials:

```bash
login {your_username}
```

Then enter your password when prompted. Assuming your credentials are valid, you will now be logged into the server.

You can now post new RFCs, revisions, and comments. Run `help` in the CLI client for a full list of commands.

## Setting Up SMTP

This step is required if you want to enable email verification of new accounts.

The following environment variables are required for SMTP delivery:

- `APP_BASE_URL` (e.g. mdrfc.example.com)
- `EMAIL_FROM` (e.g. noreply@example.com)
- `SMTP_HOST` (e.g. smtp.example.com)
- `SMTP_PORT` (default is 587)
- `SMTP_USERNAME` (your SMTP username)
- `SMTP_PASSWORD` (your SMTP password)

You can optionally tune these environment variables:

- `SMTP_STARTTLS` (default is `true`)
- `SMTP_USE_SSL` (default is `false`)

Also change `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN` to `false` (since verification tokens will now be delivered via email).

With these environment variables in place (and assuming they're valid), try launching the server:

```bash
mdrfc serve
```

Now try hitting the endpoint `POST /signup` again with new credentials--you should see that `metadata.verification_token` is now `null`. This token will be sent to the email you registered with.

After receiving the token, hit the endpoint `POST /verify-email` with the new token. Your new account should register successfully--you can now use this MDRFC server as an authorized user.

## Configuration

When running the server from the CLI (i.e. `mdrfc serve`), you can add the following options:

- `-H HOST, --host HOST`: The host to serve on (defualt is `"127.0.0.1"`).
- `-p PORT, --port PORT`: The port to serve on (default is `8026`).
- `-r, --reload`: Flag to reload on detected code changes.
- `-lf LOG_FILE, --log-file LOG_FILE`: The filepath to write logs to (default is `"mdrfc.log"`).
- `-llf LEVEL, --log-level-file LEVEL`: The minimum log level to write to the log file (default is "`INFO"`). Must be one of `["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`.
- `-llc LEVEL, --log-level-console LEVEL`: The minimum log level to write to the console (default is "`INFO"`). Must be one of `["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`.

## Endpoints

The MDRFC server provides various HTTP endpoints for RFC management, comments, and user authentication. For a comprehensive list of endpoints, see [endpoints/](/docs/endpoints/README.md).

