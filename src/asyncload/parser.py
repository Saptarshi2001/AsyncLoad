from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from .config import GlobalConfig

@dataclass
class Params:
    url: str
    numreq: int
    conreq: int
    method: str
    timemode: str | None
    body: str | None



class ProtocolParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Async load testing cli", exit_on_error=False
        )
        self.add_args()
        self.add_mutually_excusive_groups()

    def add_args(self):
        self.parser.add_argument("url", nargs="?", type=str, help="URL to load test")
        self.parser.add_argument("-history", action="store_true", help="view session history")
        self.parser.add_argument("-setup", action="store_true", help="Create global config file")
        self.parser.add_argument("-n", type=int, help="Number of total requests (overrides config)")
        self.parser.add_argument("-c", type=int, help="Number of concurrent requests (overrides config)")
        self.parser.add_argument(
            "-d",
            "--data",
            type=str,
            help="JSON body or payload for POST/PUT/PATCH/DELETE",
        )
        self.parser.add_argument("-weekly", action="store_const", const="weekly")
        self.parser.add_argument("-monthly", action="store_const", const="monthly")
        self.parser.add_argument("-yearly", action="store_const", const="yearly")

    def add_mutually_excusive_groups(self):
        httpmethods = self.parser.add_mutually_exclusive_group()
        httpmethods.add_argument("-GET", dest="method", action="store_const", const="get")
        httpmethods.add_argument("-POST", dest="method", action="store_const", const="post")
        httpmethods.add_argument("-PUT", dest="method", action="store_const", const="put")
        httpmethods.add_argument("-DELETE", dest="method", action="store_const", const="delete")
        httpmethods.add_argument("-PATCH", dest="method", action="store_const", const="patch")

    def parse(self):
        args = self.parser.parse_args()

        if args.setup:
            config_setup = GlobalConfig()
            global_config_path = config_setup.platform_path()
            config_setup.ensure_global_config()
            self.parser.exit(0, f"Global config created at: {global_config_path}")
            

        timemode = args.weekly or args.monthly or args.yearly or None
        if args.history:
            if args.url or args.method or args.n or args.c or args.data:
                self.parser.error(
                    "--history cannot be used with URL, --method, -n, -c, or -d"
                )

            print("Running history mode")
            return Params(None, None, None, None, timemode, None)
        
        if not args.url:
            self.parser.error("Error: provide a URL or use -history")

        url = args.url
        numreq = args.n if args.n is not None else int(os.getenv("TOTAL_REQUESTS", 100))
        conreq = (
            args.c if args.c is not None else int(os.getenv("CONCURRENT_REQUESTS", 10))
        )
        
        if conreq > numreq:
            self.parser.error(
                "Number of concurrent requests cannot be more than the number of total requests"
            )
        
        body = args.data if args.data is not None else None
        reqtype = args.method or os.getenv("HTTP_METHOD", "get")
        return Params(url, numreq, conreq, reqtype, timemode, body)
        
