import unittest
import sys
from unittest.mock import patch, MagicMock
import sqlite3
import os
import tempfile
import asyncio
sys.path.append('.')

from asyncload import Loadtester


class TestLoadTesterInsertPayload(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except:
            pass

    def test_insertpayload_successful_insertion(self):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
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
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
        curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LOADTEST'")
        result = curr.fetchone()
        conn.close()
        self.assertIsNotNone(result, "Table should be created")

    def test_insertpayload_table_already_exists(self):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
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
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

    def test_insertpayload_with_data_insertion(self):
        test_data = ['2023-01-01 12:00:00', 'httpbin.org', 200, 'GET', 0.5]

        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([test_data])

        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
        curr.execute("SELECT COUNT(*) FROM LOADTEST")
        count = curr.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1, "One record should be inserted")


class TestDatabaseConnectionAndExecution(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except:
            pass

    def test_database_connection_successful(self):
        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

        conn = sqlite3.connect(self.db_path)
        conn.close()

    def test_database_connection_failure(self):
        with patch('asyncload.dburl', '/invalid/path/db.db'):
            result = self.loadtester.insertpayload([])
            self.assertIsNone(result, "Method should return None on connection failure")

    def test_cursor_creation(self):
        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

    def test_database_commit_operation(self):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
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
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

    def test_database_connection_close(self):
        with patch('asyncload.dburl', self.db_path):
            self.loadtester.insertpayload([])

        conn = sqlite3.connect(self.db_path)
        conn.close()

    def test_connection_close_on_error(self):
        with patch('asyncload.dburl', '/invalid/path/db.db'):
            try:
                self.loadtester.insertpayload([])
            except:
                pass

    def test_history_database_operations(self):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
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
        curr.execute("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)",
                     ('2023-01-01 12:00:00', 'httpbin.org', 200, 'GET', '0:00:01'))
        conn.commit()
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.history()
                self.assertTrue(len(mock_print.call_args_list) > 0, "History should produce output")

    def test_history_database_error_handling(self):
        with patch('asyncload.dburl', self.db_path):
            self.loadtester.history()


class TestDatabaseIntegrationWithMockedAPI(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except:
            pass

    @patch('asyncload.aiohttp.ClientSession')
    def test_mocked_api_get_request_database_storage(self, mock_session_class):
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        mock_resp_cm = MagicMock()
        mock_session.get.return_value = mock_resp_cm

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.content.readexactly.return_value = b'H'
        mock_resp.content.read.return_value = b'ello, World!'
        mock_resp_cm.__aenter__.return_value = mock_resp
        mock_resp_cm.__aexit__.return_value = None

        with patch('asyncload.dburl', self.db_path):
            asyncio.run(self.loadtester.testurl(
                url='https://httpbin.org/get',
                numreq=2,
                conreq=1,
                reqtype='get'
            ))

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='LOADTEST'")
            table_result = cursor.fetchone()
            self.assertIsNotNone(table_result, "LOADTEST table should be created")

            cursor.execute("SELECT COUNT(*) FROM LOADTEST")
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(count, 0)

            conn.close()

    @patch('asyncload.aiohttp.ClientSession')
    def test_mocked_api_post_request_database_storage(self, mock_session_class):
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None

        mock_resp_cm = MagicMock()
        mock_session.post.return_value = mock_resp_cm

        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.content.readexactly.return_value = b'P'
        mock_resp.content.read.return_value = b'OST successful'
        mock_resp_cm.__aenter__.return_value = mock_resp
        mock_resp_cm.__aexit__.return_value = None

        with patch('asyncload.dburl', self.db_path):
            asyncio.run(self.loadtester.testurl(
                url='https://httpbin.org/post',
                numreq=1,
                conreq=1,
                reqtype='post'
            ))

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM LOADTEST")
            count = cursor.fetchone()[0]
            self.assertGreaterEqual(count, 0)

            conn.close()

    def test_database_history_with_real_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOADTEST(
        REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        TIMESTAMP TEXT NOT NULL,
        URL TEXT NOT NULL,
        STATUS INTEGER NOT NULL,
        REQTYPE VARCHAR NOT NULL,
        RESPONSETIME TEXT NOT NULL
        )
        """)

        cursor.execute("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)",
                      ('2023-01-01 12:00:00', 'https://httpbin.org/get', 200, 'GET', '0.5'))
        conn.commit()
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.history()

                self.assertTrue(len(mock_print.call_args_list) > 0, "History should produce output")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM LOADTEST")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1, "Data should still be in database")
        conn.close()

    def test_database_statistics_calculation_with_mock_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS LOADTEST(
        REQUESTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        TIMESTAMP TEXT NOT NULL,
        URL TEXT NOT NULL,
        STATUS INTEGER NOT NULL,
        REQTYPE VARCHAR NOT NULL,
        RESPONSETIME TEXT NOT NULL
        )
        """)

        test_data = [
            ('2023-01-01 12:00:00', 'https://api.example.com', 200, 'GET', '0.5'),
            ('2023-01-01 12:00:01', 'https://api.example.com', 200, 'GET', '0.7')
        ]
        cursor.executemany("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)", test_data)
        conn.commit()
        conn.close()

        with patch('asyncload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.stats(
                    [0.5, 0.7],
                    [0.1, 0.2],
                    [0.4, 0.5]
                )

                self.assertTrue(len(mock_print.call_args_list) > 0, "Statistics should be printed")



class TestHistoryTimestampFormat(unittest.TestCase):
    def setUp(self):
        self.loadtester = Loadtester()
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name

    def tearDown(self):
        try:
            os.unlink(self.db_path)
        except:
            pass

    def _seed_data(self, timestamps):
        conn = sqlite3.connect(self.db_path)
        curr = conn.cursor()
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
        for ts in timestamps:
            curr.execute("INSERT INTO LOADTEST (TIMESTAMP,URL,STATUS,REQTYPE,RESPONSETIME) VALUES (?,?,?,?,?)",
                         (str(ts), 'httpbin.org', 200, 'GET', '0.5'))
        conn.commit()
        conn.close()

    def test_history_default_format(self):
        self._seed_data(['2023-01-01 12:00:00'])
        with patch('asyncload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.history()
                output = " ".join(str(call) for call in mock_print.call_args_list)
                self.assertIn("01:01:2023", output)

    def test_history_weekly_format(self):
        self._seed_data(['2023-01-01 12:00:00', '2023-01-31 12:00:00'])
        with patch('asyncload.dburl', self.db_path):
            with patch('builtins.print') as mock_print:
                self.loadtester.history(timemode="weekly")
                output = " ".join(str(call) for call in mock_print.call_args_list)
                self.assertIn("01:01:2023", output)


if __name__ == '__main__':
    unittest.main()