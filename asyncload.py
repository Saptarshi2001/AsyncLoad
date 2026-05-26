import requests
import argparse,sys
import re
import asyncio,aiohttp
import time
from aiohttp import ClientTimeout
import logging
import sqlite3
import dotenv,os
import argparse
import json
import datetime
from logtail import LogtailHandler
import logging
import dotenv
from dotenv import load_dotenv
from config import GlobalConfig

config_setup = GlobalConfig()
load_dotenv(config_setup.platform_path())
load_dotenv("config.env")
load_dotenv(".env")

dburl = os.getenv("DATABASE_URL") or "load.db"
logging.basicConfig(level=logging.INFO)
timeout = os.getenv("timeout") or "0"
LOGTAIL_URL = os.getenv("LOGTAIL_URL") or None
LOGTAIL_TOKEN = os.getenv("LOGTAIL_TOKEN") or None

if LOGTAIL_TOKEN==None:
    print("Please setup a valid LOGTAIL TOKEN")
elif LOGTAIL_URL==None:
    print("Please use a valid LOGTAIL URL")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
handler = LogtailHandler(source_token=LOGTAIL_TOKEN, host=LOGTAIL_URL)
logger.addHandler(handler)


class Loadtester:
    def __init__(self):
        self.numreq=0
        self.conreq=0
        
               

    def read(self):
        try:
            parser=argparse.ArgumentParser(description="Async load testing cli",exit_on_error=False)

            parser.add_argument('url', nargs='?', type=str, help='URL to load test')
            parser.add_argument('-history', action='store_true')
            parser.add_argument('-setup', action='store_true', help='Create global config file')
            parser.add_argument('-n', type=int, help='Number of total requests (overrides config)')
            parser.add_argument('-c', type=int, help='Number of concurrent requests (overrides config)')
            methods=parser.add_mutually_exclusive_group()

            parser.add_argument('-weekly', action='store_const', const='weekly')
            parser.add_argument('-monthly', action='store_const', const='monthly')
            parser.add_argument('-yearly', action='store_const', const='yearly')
            methods.add_argument('-GET', dest='method', action='store_const', const='get')
            methods.add_argument('-POST', dest='method', action='store_const', const='post')
            methods.add_argument('-PUT', dest='method', action='store_const', const='put')
            methods.add_argument('-DELETE', dest='method', action='store_const', const='delete')
            methods.add_argument('-PATCH', dest='method', action='store_const', const='patch')
            parser.add_argument('-d', '--data', type=str, help="JSON body or payload for POST/PUT/PATCH/DELETE")
            args=parser.parse_args()

            if args.setup:
                ensure_global_config()
                print(f"Global config created at: {global_config_path}")
                print("Edit it with your LOGTAIL_TOKEN and other settings before running.")
                return

            timemode=args.weekly or args.monthly or args.yearly or None
            if args.history:
                if args.url or args.method or args.n or args.c:
                    print("Error: -history cannot be used with a URL or HTTP method or -n/-c")
                    return

                print("Running history mode")
                self.history(timemode)
                return

            if not args.url:
                print("Error: provide a URL or use -history")
                return

            url = args.url
            self.numreq = args.n if args.n is not None else int(os.getenv("TOTAL_REQUESTS", 100))
            self.conreq = args.c if args.c is not None else int(os.getenv("CONCURRENT_REQUESTS", 10))
            if self.conreq > self.numreq:
                print("Number of concurrent requests cannot be more than the number of total requests")
                return
            reqtype = args.method or os.getenv("HTTP_METHOD", "get")
            asyncio.run(self.testurl(url=url, numreq=self.numreq, conreq=self.conreq, reqtype=reqtype))
        except RuntimeError as e:
            logging.info("Runtime error "+ str(e))
            print("Runtime error "+str(e))
            return

        except (argparse.ArgumentError, SystemExit) as e:
            print("Invalid cli arguments:-" + str(e))
            logging.info("Error:-" + str(e))
            return
        except TypeError as e:
            print("TypeError"+ str(e))
            logging.info("TypeError:-" + str(e))
            return
        
        except AttributeError as e:
            print("AttributeError"+ str(e))
            logging.info("AttributeError:-" + str(e))
            return
        except asyncio.exceptions.IncompleteReadError as e:
            print("No data to read "+ str(e))
            logging.info("IncompleteReadError "+ str(e))
            return


    async def testurl(self,url,numreq,conreq,reqtype,headers=None):
        try:
            print("Running....")
            connector=aiohttp.TCPConnector(limit=conreq)
            successes=0
            failures=0
            totresponsetime=[]
            firstbytetime=[]
            lastbytetime=[]
            requestlist=[]
            failmsgs=[]
            responselatencies=[]
           
            async with aiohttp.ClientSession(connector=connector,timeout=ClientTimeout(float(timeout))) as session:
                async def getresult(url):
                    nonlocal successes,failures
                    try:

                        
                        t0=time.perf_counter()
                        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        async with getattr(session,reqtype)(url,headers=headers) as resp:
                            
                            try:
                                firstbyte=await resp.content.readexactly(1)
                                timetofirstbyte=time.perf_counter()-t0
                                firstbytetime.append(timetofirstbyte)
                            except asyncio.IncompleteReadError:
                                timetofirstbyte = 0  # or some default
                                firstbytetime.append(timetofirstbyte)
                            content = await resp.content.read()
                            timetolastbyte=time.perf_counter()-t0
                            endtime=time.perf_counter()
                            lastbytetime.append(timetolastbyte)
                            diff=endtime-t0
                            requestlist.append([timestamp,url,resp.status,reqtype,diff])
                            responselatencies.append(diff)
                            totresponsetime.append(diff)

                            statuscode= resp.status
                            if statuscode >=200 and statuscode<=399:
                                successes+=1
                            else:
                                failures+=1
                                body = content.decode('utf-8', errors='ignore')
                                failmsgs.append({
                                "timestamp": str(time.time_ns()),     # Loki needs nanoseconds
                                "url": url,
                                "status": resp.status,
                                "method": reqtype,
                                "body": body
                                })
                                for msg in failmsgs:

                                    logger.info(msg)
                            
                                print("Error occured!!! Please look into betterstack for more details")
                
                    except aiohttp.ClientError as e:
                        print("aiohttp exception"+ str(e))
                start_interval=time.perf_counter()
                tasks=[asyncio.create_task(getresult(url))for i in range(self.numreq)]
                await asyncio.gather(*tasks) 
                time_interval=time.perf_counter()-start_interval
            print(f"{'='*60}")
            print(f"{'Load Test Results':^60}")
            print(f"{'='*60}")
            print(f"{'Total Requests:':<25} {numreq:>10}")
            print(f"{'Concurrent Requests:':<25} {conreq:>10}")
            print(f"{'Successful Requests:':<25} {successes:>10}")
            print(f"{'Failed Requests:':<25} {failures:>10}")
            print(f"{'-'*60}")
            if reqtype in ["get","post", "put", "patch", "delete"]:
                self.insertpayload(requestlist)
            throughput=successes/time_interval
            error_rate=(failures/numreq)*100
            avg_latency=sum(requestlist)/numreq
            self.stats(totresponsetime,firstbytetime,lastbytetime,responselatencies,numreq,throughput,error_rate,avg_latency)
            
        except asyncio.TimeoutError as e:
        
            print("Timeout error "+str(e))
            logging.info("Timeout error "+str(e))
            return
        except RuntimeError as e:
            print("Runtime error "+str(e))
            logging.info("Runtime error "+str(e))
            return
        except ValueError as e:
            print("Value error "+str(e))
            logging.info("Value error "+str(e))
            return

        
    def insertpayload(self,reqlist):
        try:
            i=0
            conn=sqlite3.connect(dburl)
            curr=conn.cursor()
            if not curr.fetchone():
                curr.execute("""
        CREATE TABLE IF NOT EXISTS LOADTEST(
        REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        TIMESTAMP TEXT NOT NULL,
        URL TEXT NOT NULL,
        STATUS INTEGER NOT NULL,
        REQTYPE VARCHAR NOT NULL,
        RESPONSETIME TEXT NOT NULL
)
""")
            conn.commit()
            while i<len(reqlist):
                lst=reqlist[i]
                curr.execute("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)",(lst[0], lst[1], lst[2], lst[3], str(lst[4])))
                i+=1
                lst.insert(0,curr.lastrowid)

            
            conn.commit()
            conn.close()
            self.desc(reqlist) 
            
        except ConnectionError as e:
            print("Database error"+ str(e))
            logging.info("Database error"+ str(e))
            return
        except sqlite3.OperationalError as e:
            print("Database error"+ str(e))
            logging.info("Database error"+ str(e))
            return

            

    def history(self,timemode=None):
        try:
            conn=sqlite3.connect(dburl)
            curr=conn.cursor()
            data=curr.execute("SELECT * FROM LOADTEST").fetchall()
            conn.commit()
            conn.close()
            # Print header based on time mode
            if timemode == "weekly":
                header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<25} | {'Status':<8} | {'Method':<9} | {'Response Time':<15} | {'Week'}"
                print(header)
                print("-" * len(header))
            elif timemode == "monthly":
                header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<25} | {'Status':<8} | {'Method':<9} | {'Response Time':<15} | {'Month'}"
                print(header)
                print("-" * len(header))
            elif timemode == "yearly":
                header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<25} | {'Status':<8} | {'Method':<9} | {'Response Time':<15} | {'Year'}"
                print(header)
                print("-" * len(header))
            else:
                # Default history view without time grouping
                header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<25} | {'Status':<8} | {'Method':<9} | {'Response Time':<15}"
                print(header)
                print("-" * len(header))

            for row in data:
                try:
                    if timemode == "weekly":
                        try:
                            dt = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            dt = datetime.datetime.fromtimestamp(float(row[1]))
                        week = dt.isocalendar().week
                        print(f"{row[0]:<12} | {dt.strftime('%d:%m:%Y %H:%M:%S'):<19} | {str(row[2])[:25]:<25} | {row[3]:<8} | {str(row[4]):<9} | {str(row[5])[:15]:<15} | {week}")

                    elif timemode == "monthly":
                        try:
                            dt = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            dt = datetime.datetime.fromtimestamp(float(row[1]))
                        month = dt.month
                        print(f"{row[0]:<12} | {dt.strftime('%d:%m:%Y %H:%M:%S'):<19} | {str(row[2])[:25]:<25} | {row[3]:<8} | {str(row[4]):<9} | {str(row[5])[:15]:<15} | {month}")

                    elif timemode == "yearly":
                        try:
                            dt = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            dt = datetime.datetime.fromtimestamp(float(row[1]))
                        year = dt.year
                        print(f"{row[0]:<12} | {dt.strftime('%d:%m:%Y %H:%M:%S'):<19} | {str(row[2])[:25]:<25} | {row[3]:<8} | {str(row[4]):<9} | {str(row[5])[:15]:<15} | {year}")

                    else:
                        # Default view
                        try:
                            dt = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            dt = datetime.datetime.fromtimestamp(float(row[1]))
                        print(f"{row[0]:<12} | {dt.strftime('%d:%m:%Y %H:%M:%S'):<19} | {str(row[2])[:25]:<25} | {row[3]:<8} | {str(row[4]):<9} | {str(row[5])[:15]:<15}")

                except (ValueError, TypeError, AttributeError) as e:
                    logging.error(f"Error processing history data: {e}")
                    continue

        except sqlite3.OperationalError as e:
            logging.info("Database error: " + str(e))
            print("Database error")
            return

        except RuntimeError as e:
            logging.info("Runtime error: " + str(e))
            print("Runtime error")
            return

    def stats(self,totresponsetime,firstbytetime,lastbytetime,responselatencies,numreq,throughput,error_rate,avg_latency):
        try:

            if not totresponsetime and not firstbytetime and not lastbytetime:
                print("Error!!! No requests found")
                return
            elif not totresponsetime:
                print("Error!!! No requests found")
            elif not firstbytetime:
                print("Error!!! No first bytes found")
                return        
            elif not lastbytetime:
                print("Error!!! No last bytes found")
                return
            sorted_latencies=sorted(responselatencies)
            p99=0.99*numreq
            p95=0.95*numreq
            print("\n")
            print(f"{'Performance Statistics':^60}")
            print(f"{'-'*60}")
            print(f"{'Total Response Time (seconds)':<35}")
            print(f"{'  Maximum:':<15} {max(totresponsetime):>12.6f}")
            print(f"{'  Minimum:':<15} {min(totresponsetime):>12.6f}")
            print(f"{'  Average:':<15} {sum(totresponsetime)/len(totresponsetime):>12.6f}")
            print()
            print(f"{'First Byte Time (seconds)':<35}")
            print(f"{'  Maximum:':<15} {max(firstbytetime):>12.6f}")
            print(f"{'  Minimum:':<15} {min(firstbytetime):>12.6f}")
            print(f"{'  Average:':<15} {sum(firstbytetime)/len(firstbytetime):>12.6f}")
            print()
            print(f"{'Last Byte Time (seconds)':<35}")
            print(f"{'  Maximum:':<15} {max(lastbytetime):>12.6f}")
            print(f"{'  Minimum:':<15} {min(lastbytetime):>12.6f}")
            print(f"{'  Average:':<15} {sum(lastbytetime)/len(lastbytetime):>12.6f}")
            print(f"{'  P99 latency:':<15} {p99}")
            print(f"{'  P95 latency:':<15} {p95}")
            print(f"{'  Throughput:':<15} {throughput}")
            print(f"{'  Error rate:':<15} {error_rate}")
            print(f"{'  Average latency:':<15} {avg_latency}")
            print(f"{'='*60}")

        except RuntimeError as e:
            print("Runtime error-: "+ str(e))
            return
        

    def desc(self,reqlist):
        print(f"{'Individual Request Details':^60}")
        print(f"{'-'*60}")

        # Print table header
        header = f"{'Request ID':<12} | {'Timestamp':<19} | {'URL':<30} | {'Status':<8} | {'Method':<9} | {'Response Time'}"
        print(header)
        print("-" * len(header))

        # Print each request
        for lst in reqlist:
            reqid = lst[0]
            try:
                dt = datetime.datetime.strptime(lst[1], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.datetime.fromtimestamp(float(lst[1]))
            timestamp = dt.strftime("%d:%m:%Y %H:%M:%S")
            url = str(lst[2])[:30]        # Truncate URL if too long
            status = lst[3]
            reqtype = str(lst[4])
            responsetime = f"{lst[5]:.6f}"  # Format response time to 6 decimal places

            print(f"{reqid:<12} | {timestamp:<19} | {url:<30} | {status:<8} | {reqtype:<9} | {responsetime}")

        print(f"{'='*60}")
    # how to actually send the id as well


def main():
    config_setup.ensure_global_config()
    load_dotenv("config.env")
    load_dotenv(".env")
    load = Loadtester()
    load.read()

if __name__ == "__main__":
    main()

