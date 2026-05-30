from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Footer, Header, Label, Rule, Static
import pymongo
from datetime import datetime, timedelta
from .env import getenv


class MetricRow(Static):
    TIME_METRICS = {
        "p99",
        "p95",
        "avg_latency",
        "max_ttfb",
        "min_ttfb",
        "max_ttlb",
        "min_ttlb",
        "maxttfb",
        "minttfb",
        "maxttlb",
        "minttlb",
    }
    RATE_METRICS = {"throughput"}

    def __init__(self, name, value):
        super().__init__()
        self.metric_key = str(name)
        self.metric_name = str(name).replace("_", " ").title()
        self.metric_value = self._format_value(self.metric_key, value)

    def compose(self):
        yield Label(self.metric_name, classes="metric-name")
        yield Label(self.metric_value, classes="metric-value")

    @staticmethod
    def _format_value(name, value):
        metric_name = str(name).lower()
        if isinstance(value, float):
            if metric_name in MetricRow.TIME_METRICS:
                return f"{value:,.2f} ms"
            if metric_name in MetricRow.RATE_METRICS:
                return f"{value:,.2f} req/s"
            return f"{value:,.2f}"
        if isinstance(value, int):
            if metric_name in MetricRow.TIME_METRICS:
                return f"{value:,} ms"
            if metric_name in MetricRow.RATE_METRICS:
                return f"{value:,} req/s"
            return f"{value:,}"
        if value is None:
            return "N/A"
        return str(value)


class Terminal(App):
    CSS_PATH = "terminal.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("ctrl+q", "quit", "Quit")]
    TITLE = "AsyncLoad DashBoard"
    
    def __init__(self, metrics=None, history=None, timemode=None):
        super().__init__()
        self.metrics = metrics or {}
        self.history = history or []
        self.history_mode = history is not None
        self.timemode = timemode

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="dashboard"):
            with VerticalScroll(id="panel"):
                yield Label(self._title(), id="title")
                if self.history_mode:
                    yield from self._compose_history()
                else:
                    for name, value in self.metrics.items():
                        yield MetricRow(name, value)
        yield Footer()

    
    def _compose_history(self):
        if not self.history:
            yield Label("No history found for this time range.", classes="history-empty")
            return

        for record in self.history:
            yield MetricRow("url", record.get("url", "Unknown URL"))
            for index, metric in enumerate(record.get("metrics", [])):
                if index:
                    yield Rule(classes="history-separator")
                timestamp = metric.get("timestamp")
                yield MetricRow("timestamp", self._format_timestamp(timestamp))
                for name, value in metric.items():
                    if name != "timestamp":
                        yield MetricRow(name, value)

    def _title(self):
        if not self.history_mode:
            return "ASYNCLOAD // METRICS"
        if self.timemode:
            return f"ASYNCLOAD // {self.timemode.upper()} HISTORY"
        return "ASYNCLOAD // HISTORY"

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

    @staticmethod
    def _format_timestamp(timestamp):
        if hasattr(timestamp, "strftime"):
            return timestamp.strftime("%d-%m-%Y %H:%M:%S")
        if timestamp is None:
            return "Unknown timestamp"
        return str(timestamp)

    def displaystats(self):
        self.run()
