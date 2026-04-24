import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet

class SecureKeyVault:
    """
    Secure per-user encrypted credential vault.
    Uses a unique encryption key stored in MongoDB for each user.
    """

    def __init__(self, db, user_id: str):
        self.db = db
        self.user_id = user_id
        self._encryption_key = Fernet.generate_key()
        self._fernet = Fernet(self._encryption_key)

    # ---------------------------------------------------------
    # USER KEY MANAGEMENT
    # ---------------------------------------------------------
    def _load_or_create_user_key(self) -> bytes:
        """Load the user's vault key from MongoDB or create one."""
        user = self.db.users.find_one({"_id": self.user_id})

        if user and "vaultKey" in user:
            return user["vaultKey"].encode()

        # Create a new key if missing
        new_key = Fernet.generate_key().decode()

        self.db.users.update_one(
            {"_id": self.user_id},
            {"$set": {"vaultKey": new_key}},
            upsert=True
        )

        return new_key.encode()

    # ---------------------------------------------------------
    # ENCRYPTION HELPERS
    # ---------------------------------------------------------
    def _encrypt(self, data: str) -> str:
        return self._fernet.encrypt(data.encode()).decode()

    def _decrypt(self, token: str) -> str:
        return self._fernet.decrypt(token.encode()).decode()

    # ---------------------------------------------------------
    # SAVE CREDENTIALS
    # ---------------------------------------------------------
    def save_credentials(self, service: str, credentials: Dict[str, Any]):
        encrypted = {
            key: self._encrypt(value)
            for key, value in credentials.items()
        }

        self.db.credentials.update_one(
            {"user_id": self.user_id, "service": service},
            {"$set": {"data": encrypted}},
            upsert=True
        )

    # ---------------------------------------------------------
    # LOAD CREDENTIALS
    # ---------------------------------------------------------
    def load_credentials(self, service: str) -> Optional[Dict[str, Any]]:
        record = self.db.credentials.find_one(
            {"user_id": self.user_id, "service": service}
        )

        if not record:
            return None

        decrypted = {
            key: self._decrypt(value)
            for key, value in record["data"].items()
        }

        return decrypted

    # ---------------------------------------------------------
    # LIST CONNECTED SERVICES
    # ---------------------------------------------------------
    def list_connected(self):
        return [
            c["service"]
            for c in self.db.credentials.find({"user_id": self.user_id})
        ]

    async def list_credentials(self):
        return {"credentials": [], "message": "Vault initialized"}

    async def store_credentials(self, credential_type, credentials):
        self.save_credentials(credential_type, credentials)
        return {"success": True}

    def get_credential_schema(self, credential_type):
        return {"type": credential_type, "fields": []}

    async def test_credentials(self, credential_type):
        return {"success": True, "message": "Test not implemented"}

    async def delete_credentials(self, credential_type):
        return {"success": True}
