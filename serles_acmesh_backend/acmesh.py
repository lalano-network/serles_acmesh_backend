import os
import tempfile
import subprocess

from subprocess import STDOUT, PIPE

class AcmeSHBackend:
    """ACME.SH backend for Serles.

    Backend will pass the certificate signing request to an already configured
    ACME.SH installation using DNS-01 validation.

    Example ussage in serles config.ini:

    # Backend configuration to use AcmeSHBackend
    backend = serles_acmesh_backend:AcmeSHBackend
    
    [acmesh]
    acmesh_binary_path = /root/.acme.sh/acme.sh
    dns_plugin = dns_pdns

    # Config depends on the dns_plugin used.
    # For reference, see ACME.sh documentation:
    # https://github.com/acmesh-official/acme.sh/wiki/dnsapi
    # https://github.com/acmesh-official/acme.sh/wiki/dnsapi2

    dns_plugin_config = 
        pdns_url = https://pdns.example.com
        pdns_token = your_api_token
        pdns_serverid = localhost
        pdns_ttl = 60

    """
    
    def __init__(self, config):

        if "acmesh" not in config:
            raise Exception("acmesh section missing from config.ini")
        
        self.acmesh_binary_path = config["acmesh"].get("acmesh_binary_path", "/root/.acme.sh/acme.sh")
        if not os.access(self.acmesh_binary_path, os.X_OK):
            raise Exception(f"ACME.sh '{self.acmesh_binary_path}' not executable")
        
        self.acmesh_home_path = config["acmesh"].get("acmesh_home_path", "/root/.acme.sh")
        if not os.path.exists(self.acmesh_home_path):
            raise Exception(f"ACME.sh home path '{self.acmesh_home_path}' does not exist.")

        self.dns_plugin = config["acmesh"].get("dns_plugin", None)
        if not self.dns_plugin:
            raise Exception("Please specify a dns_plugin in acmesh section of config.ini")

        self.dns_plugin_config = config["acmesh"].get("dns_plugin_config", None)
        if not self.dns_plugin_config:
            raise Exception("Please specify a dns_plugin_config in acmesh section of config.ini")
        
        self.dns_sleep_time = config["acmesh"].get("dns_sleep_time", 300)
        self.debug_mode = config["acmesh"].get("debug_mode", False)
        

    def sign(self, csr, subjectDN, subjectAltNames, email):
        with tempfile.TemporaryDirectory(prefix="serles-acmesh") as tmpdir:
            
            csr_file = f"{tmpdir}/csr.pem"
            with open(csr_file, "wb") as fh:
                fh.write(csr)

            os.makedirs(f"{self.acmesh_home_path}/certificates/", exist_ok=True)
            fullchain_file = f"{self.acmesh_home_path}/certificates/{subjectAltNames[0]}.pem"

            cmd = [
                self.acmesh_binary_path,
                "--sign-csr",
                "--csr", csr_file,
                "--dns", self.dns_plugin,
                "--fullchain-file", fullchain_file,
                "--home", self.acmesh_home_path,
                "--dnssleep", str(self.dns_sleep_time),
            ]

            if self.debug_mode:
                cmd.append("--debug")

            # Prepare environment with DNS plugin config
            env = self._parse_dns_plugin_config(self.dns_plugin_config)

            res = subprocess.run(cmd, stdout=PIPE, stderr=STDOUT, env=env, check=False, timeout=900)
            output = res.stdout.decode("utf-8")

            # If certificate already exists, trying to return already issued certificate
            # 2 means cert already exists
            if res.returncode == 2:
                pass

            elif res.returncode != 0:
                return (None, f"acme.sh exited with error {res.returncode} and output:\n{output}")

            with open(fullchain_file, "r") as new_chain:
                return new_chain.read(), None

    def _parse_dns_plugin_config(self, config_str):
        # Parse the nested config string and create environment dict
        config_dict = {}
        for line in config_str.strip().splitlines():
            line = line.strip()
            
            # Throw Error if config is malformed
            if not line or '=' not in line:
                RuntimeError(f"Malformed dns_plugin_config line: '{line}'")
            
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            
            config_dict[key] = value

        return config_dict
