from cryptography.fernet import Fernet  # type: ignore

key = Fernet.generate_key()
print(key.decode())