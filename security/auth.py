"""Local prototype authentication with PBKDF2 password hashing and role checks.
This is suitable for a controlled localhost demonstration, not internet deployment.
"""
import hashlib, hmac, json, os, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USERS_PATH = ROOT / "database" / "users.json"
ITERATIONS = 310_000
VALID_ROLES = {"admin", "analyst", "viewer"}

def _load():
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_PATH.exists(): return {}
    try:
        data=json.loads(USERS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("User database is unreadable. Back it up and repair database/users.json.") from exc

def _save(users):
    USERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp=USERS_PATH.with_suffix('.tmp')
    temp.write_text(json.dumps(users, indent=2), encoding='utf-8')
    try: os.chmod(temp, 0o600)
    except OSError: pass
    temp.replace(USERS_PATH)

def user_count(): return len(_load())

def validate_password(password):
    if len(password) < 12: raise ValueError("Password must contain at least 12 characters.")
    if not any(c.islower() for c in password) or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
        raise ValueError("Password must include uppercase, lowercase, and a number.")

def create_user(username, password, role='viewer', created_by='system'):
    username=(username or '').strip().lower()
    if len(username) < 3 or len(username) > 40 or not username.replace('_','').replace('-','').isalnum():
        raise ValueError("Username must be 3–40 characters using letters, numbers, _ or -.")
    if role not in VALID_ROLES: raise ValueError("Invalid role.")
    validate_password(password)
    users=_load()
    if username in users: raise ValueError("That username already exists.")
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    users[username]={'salt':salt.hex(),'password_hash':digest.hex(),'iterations':ITERATIONS,'role':role,'created_by':created_by}
    _save(users)
    return {'username':username,'role':role}

def authenticate(username, password):
    username=(username or '').strip().lower()
    users=_load(); record=users.get(username)
    # Perform a PBKDF2 operation even for unknown usernames to reduce timing differences.
    salt=bytes.fromhex(record['salt']) if record else b'\0'*16
    iterations=int(record.get('iterations', ITERATIONS)) if record else ITERATIONS
    expected=bytes.fromhex(record['password_hash']) if record else b'\0'*32
    actual=hashlib.pbkdf2_hmac('sha256', (password or '').encode('utf-8'), salt, iterations)
    if not record or not hmac.compare_digest(actual, expected): return None
    return {'username':username,'role':record['role']}

def list_users():
    return [{'username':name,'role':data.get('role','viewer')} for name,data in sorted(_load().items())]

def has_role(user, *roles): return bool(user and user.get('role') in roles)
