"""Compatibility shim: prefer imports from common.event_sync."""

from common.event_sync import EventSync

__all__ = ["EventSync"]
