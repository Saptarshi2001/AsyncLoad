import unittest
from unittest.mock import MagicMock, patch

from asyncload.db import Record
from asyncload.env import Env, EnvKeys, getenv


class TestEnv(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            EnvKeys.MONGO_URL: "mongodb://localhost:27017",
            EnvKeys.MONGO_DATABASE: "asyncload",
            EnvKeys.MONGO_COLLECTION: "runs",
            EnvKeys.TIMEOUT: "10",
            EnvKeys.TOTAL_REQUESTS: "100",
            EnvKeys.CONCURRENT_REQUESTS: "10",
            EnvKeys.HTTP_METHOD: "get",
        },
        clear=True,
    )
    def test_getenv_returns_env_dataclass(self):
        env = getenv()

        self.assertEqual(
            env,
            Env(
                "mongodb://localhost:27017",
                "asyncload",
                "runs",
                "10",
                "100",
                "10",
                "get",
            ),
        )


class TestRecord(unittest.TestCase):
    @patch("asyncload.db.pymongo.MongoClient")
    @patch("asyncload.db.getenv")
    def test_insertpayload_connects_to_configured_collection(
        self, mock_getenv, mock_mongo_client
    ):
        env = MagicMock(
            MONGO_URL="mongodb://localhost:27017",
            DATABASE="asyncload",
            COLLECTION="runs",
        )
        mock_getenv.return_value = env
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client

        result = Record().insertpayload({"url": "https://example.com"})

        self.assertIsNone(result)
        mock_mongo_client.assert_called_once_with("mongodb://localhost:27017")
        mock_client.__getitem__.assert_called_once_with("asyncload")
        mock_client.__getitem__.return_value.__getitem__.assert_called_once_with("runs")


if __name__ == "__main__":
    unittest.main()
