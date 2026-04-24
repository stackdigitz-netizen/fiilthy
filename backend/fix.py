content = open("server.py", "r", encoding="utf-8").read()
old = "# key_vault initialized lazily per-request"
new = "try:\n    key_vault = SecureKeyVault(db, \"system\")\nexcept Exception as e:\n    print(f\"Warning: key_vault init failed: {e}\")\n    key_vault = None"
open("server.py", "w", encoding="utf-8").write(content.replace(old, new))
print("Done!")
