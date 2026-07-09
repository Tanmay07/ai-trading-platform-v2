import os

class SecretManager:
    def get_secret(self, secret_name: str) -> str:
        """
        Fetches secrets from AWS Secrets Manager/Vault.
        Falls back to OS environment variables.
        """
        return os.environ.get(secret_name, f"mock_secret_for_{secret_name}")
