from contextlib import contextmanager

class OpenTelemetryStub:
    @contextmanager
    def start_span(self, name: str):
        """
        Creates a distributed trace span for tracking requests across microservices.
        """
        print(f"[TRACING] Started span: {name}")
        try:
            yield
        finally:
            print(f"[TRACING] Ended span: {name}")
