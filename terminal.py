
try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, VerticalScroll
    from textual.widgets import Footer, Header, Label, Static
except ImportError as exc:
    App = object
    ComposeResult = object
    Container = None
    VerticalScroll = None
    Footer = None
    Header = None
    Label = None
    Static = object
    _TEXTUAL_IMPORT_ERROR = exc
else:
    _TEXTUAL_IMPORT_ERROR = None


class MetricRow(Static):
    def __init__(self, name, value):
        super().__init__()
        self.metric_name = str(name).replace("_", " ").title()
        self.metric_value = self._format_value(value)

    def compose(self):
        yield Label(self.metric_name, classes="metric-name")
        yield Label(self.metric_value, classes="metric-value")

    @staticmethod
    def _format_value(value):
        if isinstance(value, float):
            return f"{value:,.2f}"
        if isinstance(value, int):
            return f"{value:,}"
        if value is None:
            return "N/A"
        return str(value)


class Terminal(App):
    CSS_PATH = "terminal.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("ctrl+q", "quit", "Quit")]
    TITLE = "AsyncLoad DashBoard"
    
    def __init__(self, metrics):
        if _TEXTUAL_IMPORT_ERROR is not None:
            raise RuntimeError(
                "Textual is required to display terminal metrics. "
                "Install it with: pip install textual"
            ) from _TEXTUAL_IMPORT_ERROR
        super().__init__()
        self.metrics = metrics or {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="dashboard"):
            with VerticalScroll(id="panel"):
                yield Label("ASYNCLOAD // METRICS", id="title")
                for name, value in self.metrics.items():
                    yield MetricRow(name, value)
        yield Footer()

    def displaystats(self):
        self.run()
