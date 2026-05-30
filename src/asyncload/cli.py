import asyncio, aiohttp
import time
import logging
from dotenv import load_dotenv
from .parser import ProtocolParser
from .env import getenv
from .terminal import Terminal

class LoadRunner:
    def __init__(self):
        pass
        
    async def run(self, url, numreq, conreq, reqtype,body=None):
        try:
            env=getenv()
            timeout=env.TIMEOUT
            metrics={}
            print("Running....")
            success=0
            failures=0
            connector=aiohttp.TCPConnector(limit=conreq, limit_per_host=conreq)
            client=aiohttp.ClientSession(connector=connector,url=url,timeout=timeout)
            start_execution=time.perf_counter()
            async def execute_request(client):
                start_time=time.perf_counter()
                response=await client.request(reqtype,body)
                firstbyte=await response.content.readexactly(1)
                ttfb=time.perf_counter()-start_time
                data=await response.content.read()
                ttlb=time.perf_counter()-start_time
                metrics.setdefault("ttfb", []).append(ttfb)
                metrics.setdefault("ttlb", []).append(ttlb)
                if response.status>=200 and response.status<=399:
                    success+=1
                else:
                    failures+=1
                 
            asyncio.gather(execute_request(client) for _ in numreq)
            time_interval=time.perf_counter()-start_execution
            p99=0.99*numreq
            p95=0.95*numreq
            throughput=success/time_interval
            error_rate=(failures/numreq)*100
            ttfb_list=metrics['ttfb']
            ttlb_list=metrics['ttlb']
            maxttfb=max(ttfb_list)
            maxttlb=max(ttlb_list)
            minttfb=min(ttfb_list)
            minttlb=min(ttlb_list)
            metrics.__delitem__('ttfb')
            metrics.__delitem__('ttlb')
            metrics['p99']=p99
            metrics['p95']=p95
            metrics['throughput']=throughput
            metrics['error_rate']=error_rate
            metrics['maxttfb']=maxttfb
            metrics['maxttlb']=maxttlb
            metrics['minttfb']=minttfb
            metrics['minttlb']=minttlb
            metrics['success']=success
            metrics['failures']=failures
            metrics['numreq']=numreq
            metrics['conreq']=conreq
            terminal=Terminal(metrics)
            terminal.displaystats()

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


    def view_session_history(self,timemode=None):
        pass



def main():
    load_dotenv("config.env")
    load_dotenv(".env")
    parser = ProtocolParser()
    Params = parser.parse()
    url=Params.url
    numreq=Params.numreq
    conreq=Params.conreq
    reqtype=Params.method
    timemode=Params.timemode
    body=Params.body
    async_cli = LoadRunner()
    if url is None and numreq is None and conreq is None and reqtype is None:
        async_cli.view_session_history(timemode)
    else:
        asyncio.run(async_cli.run(url, numreq, conreq, reqtype,body))



if __name__ == "__main__":
    main()
