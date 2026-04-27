content = open("server.py", "r", encoding="utf-8").read()
old = """        return await key_vault.list_credentials()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))"""
new = """        if key_vault is None:
            raise HTTPException(status_code=503, detail="Vault not available")
        return await key_vault.list_credentials()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))"""
open("server.py", "w", encoding="utf-8").write(content.replace(old, new))
print("Done!")
