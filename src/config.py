import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'

class Config:
    def __init__(self):
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            env_vars = dotenv_values(env_path)
            for key, value in env_vars.items():
                setattr(self, key, self._cast_value(value))

    @staticmethod
    def _cast_value(val: str):
        if val is None:
            return None

        try:
            return int(val)
        except ValueError:
            pass

        try:
            return float(val)
        except ValueError:
            pass

        if val.lower() in ('true', 'yes', '1'):
            return True
        if val.lower() in ('false', 'no', '0'):
            return False

        return val

    @property
    def DATABASE_URL(self) -> str:
        user     = getattr(self, 'DB_USER', 'postgres')
        password = getattr(self, 'DB_PASSWORD', 'postgres')
        host     = getattr(self, 'DB_HOST', 'localhost')
        port     = getattr(self, 'DB_PORT', '5432')
        name     = getattr(self, 'DB_NAME', 'library_db')

        return f"postgresql://{user}:{password}@{host}:{port}/{name}"

config = Config()
