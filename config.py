import os, sys


class GlobalConfig:
    def __init__(self):
        self.global_config_path = None

    def platform_path(self):
        if sys.platform == "win32":
            self.global_config_path = os.path.expandvars(
                "%LOCALAPPDATA%/asyncload/config.env"
            )

        elif sys.platform == "linux":
            self.global_config_path = os.path.expanduser(
                "~/.config/asyncload/config.env"
            )

        elif sys.platform == "darwin":
            self.global_config_path = os.path.expanduser(
                "~/Library/Application Support/asyncload/config.env"
            )

        return self.global_config_path

    def ensure_global_config(self):
        if not os.path.exists(self.global_config_path):
            os.makedirs(os.path.dirname(self.global_config_path), exist_ok=True)
        with open(self.global_config_path, "w") as f:
            f.write("""# Global config for AsyncLoad  
            MONGO_URL=
    MONGO_DATABASE=
    MONGO_COLLECTION=
    TIMEOUT=0
    TOTAL_REQUESTS=100
    CONCURRENT_REQUESTS=10
    HTTP_METHOD=get

            """)
