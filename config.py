
import os,sys
class GlobalConfig:
    def __init__(self):
        self.global_config_path=None

    
    def platform_path(self):
        if sys.platform == "win32":
            self.global_config_path = os.path.expandvars("%LOCALAPPDATA%/asyncload/config.env")
        
        else:
            self.global_config_path = os.path.expanduser("~/.config/asyncload/config.env")
        
        return self.global_config_path
    

    def ensure_global_config(self):

        if not os.path.exists(self.global_config_path):
            os.makedirs(os.path.dirname(self.global_config_path), exist_ok=True)
        with open(self.global_config_path, "w") as f:
            f.write("""# Global config for AsyncLoad
            LOGTAIL_TOKEN=your_token_here
            LOGTAIL_URL=your_url_here   
            TOTAL_REQUESTS=100
            CONCURRENT_REQUESTS=10
            HTTP_METHOD=get
            DATABASE_URL=load.db
            timeout=0
            """)