import requests
import argparse, sys
import re
import asyncio, aiohttp
import time
from aiohttp import ClientTimeout
import logging
import sqlite3
import dotenv, os
import argparse
import json
import pymongo
import datetime
import logging
import dotenv
from dotenv import load_dotenv
from config import GlobalConfig
from parser import ProtocolParser
from env import Env

class AsyncLoad:
    def __init__(self):
        pass
        

    async def testurl(self, url, numreq, conreq, reqtype):
        try:
            print("Running....")

                        
        except asyncio.TimeoutError as e:
            print("Timeout error " + str(e))
            logging.info("Timeout error " + str(e))
            return
        except RuntimeError as e:
            print("Runtime error " + str(e))
            logging.info("Runtime error " + str(e))
            return
        except ValueError as e:
            print("Value error " + str(e))
            logging.info("Value error " + str(e))
            return


        
    def insertpayload(self,kv):  # a key value through which we store it in mongodb.Now we can add as many key value store as we want ,but the collc wodnt care about it. the url endpoint and then the values ,that url endpoint structure should stay intact
        
        env=Env()
        client=pymongo.MongoClient(env.URL)
        db=client[env.DATABASE]
        collc=db[env.COLLECTION]
        collc
        pass
        
            

    def view_session_history(self,timemode=None):
        pass


    def display_stats(self):
        
        sorted_latencies=sorted(responselatencies)
        p99=0.99*numreq
        p95=0.95*numreq
        print("\n")
        print(f"{'Performance Statistics':^60}")
        print(f"{'-'*60}")
        #print(f"{'Total Response Time (seconds)':<35}")
        print(f"{' Total Response Time (seconds) Maximum:':<35} {max(totresponsetime):>12.6f}")
        print(f"{' Total Response Time (seconds) Minimum:':<35} {min(totresponsetime):>12.6f}")
        print(f"{' Total Response Time (seconds) Average:':<35} {sum(totresponsetime)/len(totresponsetime):>12.6f}")
        print(f"{' First Byte Time (seconds)  Maximum:':<35} {max(firstbytetime):>12.6f}")
        print(f"{' First Byte Time (seconds)  Minimum:':<35} {min(firstbytetime):>12.6f}")
        print(f"{' First Byte Time (seconds) Average:':<35} {sum(firstbytetime)/len(firstbytetime):>12.6f}")
        print(f"{' Last Byte Time (seconds) Maximum:':<35} {max(lastbytetime):>12.6f}")
        print(f"{' Last Byte Time (seconds) Minimum:':<35} {min(lastbytetime):>12.6f}")
        print(f"{' Last Byte Time (seconds) Average:':<35} {sum(lastbytetime)/len(lastbytetime):>12.6f}")
        print(f"{' P99 latency:':<15} {p99}")
        print(f"{' P95 latency:':<15} {p95}")
        print(f"{' Throughput:':<15} {throughput}")
        print(f"{' Error rate:':<15} {error_rate}")
        print(f"{' Average latency:':<15} {avg_latency}")

def main():
    load_dotenv("config.env")
    load_dotenv(".env")

    timeout = os.getenv("timeout") or "0"
    parser = ProtocolParser()
    url, numreq, conreq, reqtype, timemode = parser.parse()
    async_cli = AsyncLoad()
    if url is None and numreq is None and conreq is None and reqtype is None:
        async_cli.view_session_history(timemode)
    else:
        async_cli.run(url, numreq, conreq, reqtype)


if __name__ == "__main__":
    main()
