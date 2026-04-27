content = open("server.py", "r", encoding="utf-8").read()
old = "try:`n    key_vault = SecureKeyVault(db, \"system\")`nexcept Exception as e:`n    print(f\"Warning: key_vault init failed: {e}\")`n    key_vault = None"
new = "try:\n    key_vault = SecureKeyVault(db, \"system\")\nexcept Exception as e:\n    print(f\"Warning: key_vault init failed: {e}\")\n    key_vault = None"
result = content.replace(old, new)
open("server.py", "w", encoding="utf-8").write(result)
print("Done!")
