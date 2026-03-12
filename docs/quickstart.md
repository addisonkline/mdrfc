# MDRFC Setup

This document contains instructions on how to download, install, and set up an MDRFC instance.

## 1. Prerequisites

- Python version 3.12 or higher
- The [`uv`](https://github.com/astral-sh/uv) package manager

## 2. Download and Install

First, clone the repository from GitHub:

```bash
git clone https://github.com/addisonkline/mdrfc
```

Next, go to the project and install the required Python dependencies:

```bash
cd mdrfc
uv venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Now try and run the project script:

```bash
mdrfc --help
```

You should see the MDRFC CLI help message. If the command failed, make sure your environment is set up and installed properly.

## 3. Environment Variables

Refer to the file `.env.example` in the project root to see which environment variables are required:

```env
# MDRFC server
## database integration
DATABASE_URL=str

## JWT auth
SECRET_KEY=str
JWT_ALGORITHM=str
ACCESS_TOKEN_EXPIRE_MINUTES=int

## SMTP stuff
APP_BASE_URL=str
EMAIL_FROM=str
SMTP_HOST=str

## utils
AUTH_DEBUG_RETURN_VERIFICATION_TOKEN=bool

# MDRFC client
MDRFC_USERNAME=str
MDRFC_PASSWORD=str
```

We will focus on just the required variables for the server for now.

Start by setting `JWT_ALGORITHM` to `"HS256"` and `ACCESS_TOKEN_EXPIRE_MINUTES` to `30`. Then, generate and set the `SECRET_KEY` to a string that is ideally longer than 32 characters. You can generate one with the following command:

```bash
openssl rand -hex 32
```

Next, connect your existing PostgreSQL database by setting the variable `DATABASE_URL`.

Finally, set `AUTH_DEBUG_RETURN_VERIFICATION_TOKEN` to `true`--we don't want to worry about SMTP email handling right now.

## 4. Running the Server

With your environment variables set, try starting the server up:

```bash
mdrfc serve
```

You should see the the server start up successfully. It is hosted on `http://localhost:8026` by default. Press `Ctrl+C` to shut it down.

## 5. Running the Client

With the server running, open another terminal and connect to it using the MDRFC client:

```bash
mdrfc client http://localhost:8026 --no-login
```

You should enter the CLI client, connected to your server. Try pinging the server:

```bash
ping -v
```

You should get a response like the following:

```
name: mdrfc
version: 0.1.0
status: ok
uptime: 10.0
metadata: {}
```

Congratulations, you have now set up an MDRFC server and connected to it with the client!

## 6. Next Steps

- More detailed server setup options and instructions: [server.md](/docs/server.md)
- More detailed client configuration options: [client.md](/docs/client.md)