import datetime

import datetime

users = {}  # username -> {password_hash, other user data}
tokens = {}  # token -> {username, expires_at}
tasks_db = {}  # username -> {task_id -> task_data}
running_instances = {}  # username -> {task_id -> {instance_data, started_at}}

TOKEN_TTL = datetime.timedelta(hours=10)