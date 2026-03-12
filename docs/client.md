# MDRFC Client Documentation

This document contains instructions on how to set up, configure, and use the MDRFC client through the CLI.

## Setup

First, follow [quickstart.md](/docs/quickstart.md) for instructions on downloading/installing MDRFC and setting the necessary environment variables.

If using your own server, ensure that it is set up, configured, and running properly (see [server.md](/docs/server.md) for more info).

You can add your account username and password as environment variables to enable auto-login on client startup:

```env
MDRFC_USERNAME="your_username"
MDRFC_PASSWORD="your_password"
```

With these variables set, connect to the server with the client:

```bash
mdrfc client {server_url}
```

You should enter the CLI client REPL logged in with your credentials (assuming they're valid). To log out of the server without disconnecting, enter `logout` (you can `login` again with the same or different credentials). To close the CLI client, enter `exit` or `quit`. 

## CLI Client

The MDRFC CLI client is a terminal-based client for accessing a given MDRFC server. It supports commands for all corresponding HTTP endpoints on the server. 

For a full list of commands that can be used in the CLI client, enter `help` or `?`.

For help with a specific command, enter `{command} -h`.