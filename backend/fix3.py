content = open("ai_services/key_vault.py", "r", encoding="utf-8").read()
new_init = """    def __init__(self, db, user_id: str):
        self.db = db
        self.user_id = user_id
        self._encryption_key = Fernet.generate_key()
        self._fernet = Fernet(self._encryption_key)"""
import re
content = re.sub(r"    def __init__.*?self\._fernet = Fernet\(self\._encryption_key\)", new_init, content, flags=re.DOTALL)
open("ai_services/key_vault.py", "w", encoding="utf-8").write(content)
print("Done!")
