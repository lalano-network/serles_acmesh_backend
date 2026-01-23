# Serles ACME.SH Backend

A backend addon for [serles-acme](https://github.com/dvtirol/serles-acme) that integrates with [acme.sh](https://github.com/acmesh-official/acme.sh) to issue certificates using DNS-01 validation.

## Overview

This backend passes certificate signing requests to an already configured ACME.SH installation, leveraging acme.sh's extensive DNS provider support for automated certificate issuance.

## Prerequisites

- Python 3.6+
- [acme.sh](https://github.com/acmesh-official/acme.sh) installed and configured
- A supported DNS provider configured with acme.sh
- [serles-acme](https://github.com/dvtirol/serles-acme) installed

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/lalano-network/serles_acmesh_backend.git
```

Or install a specific version/tag:

```bash
pip install git+https://github.com/lalano-network/serles_acmesh_backend.git@v0.1.0
```

Or add to your `requirements.txt`:

```
serles_acmesh_backend @ git+https://github.com/lalano-network/serles_acmesh_backend.git
```

After installation, ensure acme.sh is installed for your user (typically in `~/.acme.sh/`):
```bash
acme.sh -h
```

## Configuration

Add the following to your serles `config.ini`:

```ini
[DEFAULT]
# Backend configuration to use AcmeSHBackend
backend = serles_acmesh_backend:AcmeSHBackend

[acmesh]
# Path to acme.sh binary (default: /root/.acme.sh/acme.sh)
acmesh_binary_path = /root/.acme.sh/acme.sh

# Path to acme.sh home directory (default: /root/.acme.sh)
acmesh_home_path = /root/.acme.sh

# DNS plugin to use (required)
# See: https://github.com/acmesh-official/acme.sh/wiki/dnsapi
dns_plugin = dns_pdns

# DNS sleep time in seconds (default: None)
# Time to wait for DNS propagation
# If no wait time is specified in the config,
# the "--dnssleep" parameter is not used
dns_sleep_time = 300

# Enable debug mode (default: False)
debug = False

# DNS plugin configuration (required)
# Configuration depends on the dns_plugin used
# For reference, see ACME.sh documentation:
# https://github.com/acmesh-official/acme.sh/wiki/dnsapi
dns_plugin_config = 
    pdns_url = https://pdns.example.com
    pdns_token = your_api_token
    pdns_serverid = localhost
    pdns_ttl = 60
```

## DNS Provider Configuration Examples

### PowerDNS
```ini
dns_plugin = dns_pdns
dns_plugin_config = 
    pdns_url = https://pdns.example.com
    pdns_token = your_api_token
    pdns_serverid = localhost
    pdns_ttl = 60
```

### Cloudflare
```ini
dns_plugin = dns_cf
dns_plugin_config = 
    CF_Token = your_cloudflare_api_token
    CF_Account_ID = your_account_id
```

### Amazon Route53
```ini
dns_plugin = dns_aws
dns_plugin_config = 
    AWS_ACCESS_KEY_ID = your_access_key
    AWS_SECRET_ACCESS_KEY = your_secret_key
```

For a complete list of supported DNS providers and their configuration, see the [acme.sh DNS API documentation](https://github.com/acmesh-official/acme.sh/wiki/dnsapi).

## Configuration Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `acmesh_binary_path` | No | `/root/.acme.sh/acme.sh` | Path to the acme.sh executable |
| `acmesh_home_path` | No | `/root/.acme.sh` | Path to the acme.sh home directory |
| `dns_plugin` | Yes | - | DNS plugin name (e.g., `dns_cf`, `dns_pdns`) |
| `dns_plugin_config` | Yes | - | Plugin-specific configuration variables |
| `dns_sleep_time` | No | `300` | Seconds to wait for DNS propagation |
| `debug` | No | `False` | Enable acme.sh debug output |

## How It Works

1. Serles receives a certificate signing request (CSR)
2. Serles verifies the request from the client itself with an ACME challenge.
3. After that successful verification, it calls acme.sh with the appropriate DNS plugin and configuration.

4. acme.sh performs DNS-01 validation and obtains the certificate.
5. The full certificate chain is returned to the client.

## Troubleshooting

### Certificate Already Exists

If an certificate already exists in the acme.sh backend, it returns the already existing certificate.

Currently there is no other way to force renew a certificate, besides deleting the certificate files in the acme.sh backend.

`rm -rf <acmesh_home_path>/<certificate_folder>`

### DNS Propagation Issues

If validation fails due to DNS propagation:
- Increase `dns_sleep_time` in your configuration
- Check your DNS provider's propagation time
- Verify your DNS plugin configuration is correct

### Permission Issues

Ensure the user running serles has:
- Execute permissions on the acme.sh binary
- Read/write access to the acme.sh home directory
- Proper environment variables for the DNS provider

### Debug Mode

Enable debug mode for using acme.sh's internal Debug mode:
```ini
debug_mode = True
```


## Contributing

Contributions are welcome! Please submit issues and pull requests.

**The project is currently in best‑effort maintenance mode.**

## Links

- [serles-acme](https://github.com/dvtirol/serles-acme)
- [acme.sh](https://github.com/acmesh-official/acme.sh)
- [acme.sh DNS API Documentation](https://github.com/acmesh-official/acme.sh/wiki/dnsapi)
