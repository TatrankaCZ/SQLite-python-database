import subprocess
import os
FILE_SCHEMA = "./prisma.test.schema"

os.remove("test.db")
# Spuštění příkazu prisma generate s vlastním .schema souborem
subprocess.run(["prisma", "generate", f"--schema={FILE_SCHEMA}"], check=True)

# Spuštění příkazu prisma db push s vlastním .schema souborem
subprocess.run(["prisma", "db", "push",  f"--schema={FILE_SCHEMA}"], check=True)
