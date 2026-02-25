from pwdlib import PasswordHash

hash_algorithm = PasswordHash.recommended()


def verify_password(plaintxt_password: str, hash_password: str) -> bool:
    return hash_algorithm.verify(plaintxt_password, hash_password)


def calculate_hash(password: str) -> str:
    return hash_algorithm.hash(password)
