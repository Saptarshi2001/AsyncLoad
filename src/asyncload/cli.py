import asyncio
import aiohttp
import time
import logging
from dotenv import load_dotenv
from .parser import ProtocolParser
from .env import getenv
from .terminal import Terminal
from .db import Record

class LoadRunner:
    def __init__(self):
        pass
        
    async def run(self, url, numreq, conreq, reqtype, body=None)-> dict:
        try:
            env = getenv()
            timeout = aiohttp.ClientTimeout(total=float(env.TIMEOUT))
            metrics = {}
            print("Running....")
            success = 0
            failures = 0
            connector = aiohttp.TCPConnector(limit=conreq, limit_per_host=conreq)
            client = aiohttp.ClientSession(connector=connector, timeout=timeout)
            start_execution = time.perf_counter()

            async def execute_request(client):
                nonlocal success, failures
                response = None
                start_time = time.perf_counter()
                try:
                    response = await client.request(reqtype, url, json=body)
                    await response.content.read(1)
                    ttfb = time.perf_counter() - start_time
                    await response.content.read()
                    ttlb = time.perf_counter() - start_time
                    metrics.setdefault("ttfb", []).append(ttfb)
                    metrics.setdefault("ttlb", []).append(ttlb)
                    if  response.status>=200 and response.status <= 399:
                        success += 1
                    else:
                        failures += 1
                except Exception:
                    failures += 1
                finally:
                    if response is not None:
                        response.close()

            try:
                await asyncio.gather(*(execute_request(client) for _ in range(numreq)))
            finally:
                await client.close()
            
            time_interval = time.perf_counter() - start_execution

            ttfb_list = metrics.get("ttfb", [])
            ttlb_list = metrics.get("ttlb", [])
            
            if not ttlb_list or not ttfb_list:
                raise RuntimeError("No successful request timings were collected")

            sorted_ttlb = sorted(ttlb_list)
            p95 = sorted_ttlb[int((len(sorted_ttlb) - 1) * 0.95)] * 1000
            p99 = sorted_ttlb[int((len(sorted_ttlb) - 1) * 0.99)] * 1000
            throughput = success / time_interval
            error_rate = (failures / numreq) * 100
            maxttfb = max(ttfb_list) * 1000
            minttfb = min(ttfb_list) * 1000
            maxttlb = max(ttlb_list) * 1000
            minttlb = min(ttlb_list) * 1000
            avg_latency = (sum(ttlb_list) / len(ttlb_list)) * 1000

            metrics.clear()
            metrics["url"] = url
            metrics["p99"] = p99
            metrics["p95"] = p95
            metrics["throughput"] = throughput
            metrics["error_rate"] = error_rate
            metrics["maxttfb"] = maxttfb
            metrics["maxttlb"] = maxttlb
            metrics["minttfb"] = minttfb
            metrics["minttlb"] = minttlb
            metrics["success"] = success
            metrics["failures"] = failures
            metrics["numreq"] = numreq
            metrics["conreq"] = conreq
            metrics["avg_latency"] = avg_latency
            rec = Record()
            rec.insertmetrics(metrics)
            return metrics
            

        except asyncio.TimeoutError as e:
            raise TimeoutError("Timeout error " + str(e))
            
        except RuntimeError as e:
            raise RuntimeError("Runtime error " + str(e))
            


def main():
    load_dotenv("config.env")
    load_dotenv(".env")
    parser = ProtocolParser()
    params = parser.parse()
    url = params.url
    numreq = params.numreq
    conreq = params.conreq
    reqtype = params.method
    timemode = params.timemode
    body = params.body
    async_cli = LoadRunner()
    if url is None and numreq is None and conreq is None and reqtype is None:
        rec = Record()
        history = rec.getmetrics(timemode)
        terminal = Terminal(history=history, timemode=timemode)
        terminal.displaystats()
    else:
        metrics=asyncio.run(async_cli.run(url, numreq, conreq, reqtype, body))
        terminal = Terminal(metrics)
        terminal.displaystats()


if __name__ == "__main__":
    main()
