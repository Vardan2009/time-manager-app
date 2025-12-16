import datetime

users = {}  # username -> {password_hash}
tokens = {}  # token -> {username, expires_at}

TOKEN_TTL = datetime.timedelta(hours=10)
