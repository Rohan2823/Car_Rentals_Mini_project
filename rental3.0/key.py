import secrets
import string

def generate_secret_key(length=24):
    """Generate a secure random secret key."""
    charset = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(charset) for _ in range(length))

# Example usage:
secret_key = generate_secret_key()
print("Generated Secret Key:", secret_key)
