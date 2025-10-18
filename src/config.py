import os
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgres://", 1)

if db_url and "?" in db_url:
    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)
    if 'sslmode' in query_params:
        del query_params['sslmode']
    new_query = urlencode(query_params, doseq=True)
    db_url = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

TORTOISE = {
    "connections": {
        "default": db_url
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "Asia/Kolkata"
}

POSTGRESQL = {}

EXTENSIONS = (
    "cogs.events",
    "cogs.esports",
    "cogs.mod",
    "cogs.premium",
    "cogs.quomisc",
    "cogs.reminder",
    "cogs.utility",
    "jishaku",
)

DISCORD_TOKEN ="MTQyNjE4MTQ0MTA0MTA3MjE1OA.Gn12LL.LmeiJFxCSQRJCBuLHnkboMhSIlGivJrgbIZZOU"

COLOR = 0x00FFB3

FOOTER = "wolf is lub!"

PREFIX = "w"

SERVER_LINK = os.getenv("SERVER_LINK", "https://discord.gg/qXNWfdJpFd")

DEVS = tuple(map(int, os.getenv("DEVS", "985731890193502269").split(","))) if os.getenv("DEVS") else (985731890193502269,)

ERROR_LOG = os.getenv("ERROR_LOG", "")
SHARD_LOG = os.getenv("SHARD_LOG", "")
PUBLIC_LOG = os.getenv("PUBLIC_LOG", "")

SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
FASTAPI_URL = os.getenv("FASTAPI_URL", f"http://localhost:{SERVER_PORT}")
FASTAPI_KEY = os.getenv("FASTAPI_KEY", "")

SERVER_ID = int(os.getenv("SERVER_ID", "0")) if os.getenv("SERVER_ID") else 0
VOTER_ROLE = int(os.getenv("VOTER_ROLE", "0")) if os.getenv("VOTER_ROLE") else 0
PREMIUM_ROLE = int(os.getenv("PREMIUM_ROLE", "0")) if os.getenv("PREMIUM_ROLE") else 0

PRIME_EMOJI = "⭐"
