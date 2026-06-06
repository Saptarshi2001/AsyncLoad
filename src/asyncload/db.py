import pymongo
from .env import getenv
from datetime import datetime
from datetime import timedelta
from pymongo import ASCENDING
from pymongo.errors import PyMongoError


class Record:

    def __init__(self):
        pass
            

    def insertmetrics(self,url, metrics):
        env = getenv()
        client = pymongo.MongoClient(env.MONGO_URL)
        db = client[env.DATABASE]
        collc=db[env.COLLECTION]
        
        try:
            collc.create_index([("metrics.timestamp", ASCENDING)])
            collc.update_one(
                {"url": url},
                {
                    "$push": {
                        "metrics": {
                            "timestamp": datetime.now(),
                            "p99": metrics["p99"],
                            "p95": metrics["p95"],
                            "throughput": metrics["throughput"],
                            "avg_latency": metrics["avg_latency"],
                            "max_ttfb": metrics["maxttfb"],
                            "min_ttfb": metrics["minttfb"],
                            "max_ttlb": metrics["maxttlb"],
                            "min_ttlb": metrics["minttlb"],
                            "successes": metrics["success"],
                            "failures": metrics["failures"],
                            "number_of_requests": metrics["numreq"],
                            "number_of_concurrent_requests": metrics["conreq"],
                        }
                    }
                },
                upsert=True,
            )
        except PyMongoError as exc:
            print("Timeout error")
            return
        finally:
            client.close()

    def getmetrics(self, timemode=None):
        start, end = self._time_range(timemode)
        env = getenv()
        client = pymongo.MongoClient(env.MONGO_URL)
        db = client[env.DATABASE]
        collc=db[env.COLLECTION]
        try:
            return list(
                collc.aggregate(
                    [
                        {
                            "$project": {
                                "url": 1,
                                "metrics": {
                                    "$filter": {
                                        "input": {"$ifNull": ["$metrics", []]},
                                        "as": "metric",
                                        "cond": {
                                            "$and": [
                                                {"$gte": ["$$metric.timestamp", start]},
                                                {"$lte": ["$$metric.timestamp", end]},
                                            ]
                                        },
                                    }
                                },
                            }
                        },
                        {"$match": {"metrics.0": {"$exists": True}}},
                    ]
                )
            )
        except PyMongoError as exc:
            print("Timeout error:")
            return
        finally:
            client.close()

    @staticmethod
    def _time_range(timemode=None):
        now = datetime.now()
        if timemode == "weekly":
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        elif timemode == "monthly":
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif timemode == "yearly":
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = datetime.min
        return start, now
