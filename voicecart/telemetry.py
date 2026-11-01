"""Opt-in per-request numeric timing, without transcripts, SQL or credentials."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps


@dataclass
class Trace:
    spans: list[dict] = field(default_factory=list)


_active: ContextVar[Trace | None] = ContextVar("voicecart_trace", default=None)


@contextmanager
def measurements():
    trace = Trace()
    token = _active.set(trace)
    try:
        yield trace
    finally:
        _active.reset(token)


@contextmanager
def span(name: str):
    trace = _active.get()
    if trace is None:
        yield
        return
    start = time.perf_counter()
    outcome = "ok"
    try:
        yield
    except BaseException:
        outcome = "error"
        raise
    finally:
        if len(trace.spans) < 1000:
            trace.spans.append(
                {
                    "stage": name,
                    "seconds": time.perf_counter() - start,
                    "outcome": outcome,
                }
            )


def timed(name):
    def decorate(function):
        @wraps(function)
        def invoke(*args, **kwargs):
            with span(name):
                return function(*args, **kwargs)

        return invoke

    return decorate


def inference_metrics(response: dict):
    trace = _active.get()
    if trace is None:
        return
    for field_name in (
        "total_duration",
        "load_duration",
        "prompt_eval_duration",
        "eval_duration",
    ):
        value = response.get(field_name)
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and 0 <= value <= 10**15
            and len(trace.spans) < 1000
        ):
            trace.spans.append(
                {
                    "stage": "ollama." + field_name,
                    "seconds": value / 10**9,
                    "outcome": "runtime_reported",
                }
            )
