"""Central render/animation scheduler for HN BlackBox.

The scheduler is deliberately UI-framework agnostic: Tk's event loop invokes one
master tick and this module decides which channels are due. Visual channels are
retained-state updates, not timer-owned widgets. Heavy non-visual work stays in
worker pools and returns immutable data snapshots to the UI thread.
"""
from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, Dict, List, Optional


@dataclass(slots=True)
class Channel:
    callback: Callable[[], None]
    interval_ms: float = 16.67
    enabled: bool = True
    next_at: float = 0.0
    priority: int = 0
    error_count: int = 0
    last_error: str = ""


class RenderScheduler:
    """Single-clock scheduler with frame budgeting and adaptive cadence."""

    def __init__(self, target_fps: int = 60, budget_ms: float = 10.0) -> None:
        self.target_fps = max(30, min(144, int(target_fps)))
        self.budget_ms = max(2.0, float(budget_ms))
        self.frame = 0
        self.last_frame_ms = 0.0
        self.avg_frame_ms = 0.0
        self._channels: Dict[str, Channel] = {}
        self._started = time.monotonic()

    @property
    def frame_interval_ms(self) -> float:
        return 1000.0 / self.target_fps

    def register(self, name: str, callback: Callable[[], None], *, fps: float = 60.0, priority: int = 0) -> None:
        fps = max(1.0, min(float(self.target_fps), fps))
        now = time.monotonic()
        self._channels[name] = Channel(callback, 1000.0 / fps, True, now, priority)

    def unregister(self, name: str) -> None:
        self._channels.pop(name, None)

    def set_enabled(self, name: str, enabled: bool) -> None:
        ch = self._channels.get(name)
        if ch:
            ch.enabled = bool(enabled)

    def clear(self) -> None:
        self._channels.clear()

    def tick(self) -> float:
        """Run every due visual channel; V26 deliberately favors continuity over frame budgeting."""
        now = time.monotonic()
        started = time.perf_counter()
        due = [c for c in self._channels.values() if c.enabled and now >= c.next_at]
        due.sort(key=lambda c: c.priority, reverse=True)
        for ch in due:
            try:
                ch.callback()
            except Exception as exc:
                # A faulty visual channel must never poison the master clock.
                # Record the fault, keep that channel scheduled, and continue every
                # other visual channel in the same frame. This is the autonomous
                # isolation boundary: one widget can fail without freezing the HUD.
                ch.error_count += 1
                ch.last_error = f"{type(exc).__name__}: {exc}"
            finally:
                # Keep time based cadence; avoid timer drift accumulating from work cost.
                ch.next_at = now + ch.interval_ms / 1000.0
        elapsed = (time.perf_counter() - started) * 1000.0
        self.last_frame_ms = elapsed
        self.avg_frame_ms = elapsed if self.frame == 0 else (self.avg_frame_ms * 0.90 + elapsed * 0.10)
        self.frame += 1
        # V26 autonomous mode: do not downgrade or pause channels under load.
        # The next master tick stays at the target frame cadence.
        return self.frame_interval_ms

    def stats(self) -> dict:
        return {
            "target_fps": self.target_fps,
            "frame": self.frame,
            "last_frame_ms": self.last_frame_ms,
            "avg_frame_ms": self.avg_frame_ms,
            "channels": len(self._channels),
            "channel_errors": sum(c.error_count for c in self._channels.values()),
            "last_channel_errors": {name: c.last_error for name, c in self._channels.items() if c.last_error},
            "uptime_s": time.monotonic() - self._started,
        }
