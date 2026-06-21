#!/usr/bin/env python
"""Helper utilities for scenario event logging.

Provides TriggerLogger to append trigger events into per-participant scenario JSON files
located under _plog/<participant_id>/<Snn>_trigger_log.json
"""
import os
import json
import re
import datetime

# ---------------------------------------------------------------------------
# Simple trigger logging utilities (used by events_scenario scripts)
# ---------------------------------------------------------------------------
def parse_logging_arg(txt):
    import re
    if not txt:
        return (None, None)
    try:
        t = str(txt).strip()
        t = t.strip('()')
        parts = [p.strip() for p in re.split('[,;]+', t) if p.strip()]
        pid = parts[0] if len(parts) >= 1 else None
        scen = parts[1] if len(parts) >= 2 else None
        return (pid, scen)
    except Exception:
        return (None, None)


def _find_participant_dir_for_events(pid_token):
    # plog root is one level above the scenario_events package
    plog_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_plog'))
    if not pid_token:
        return None
    try:
        import re
        if re.match(r'^[Pp]_?\d{1,2}_\d{8}_\d{4}$', pid_token):
            candidate = os.path.join(plog_root, pid_token)
            if os.path.isdir(candidate):
                return candidate
            return None
    except Exception:
        pass

    norm_prefix = pid_token.replace('_', '').lower()
    try:
        for d in sorted(os.listdir(plog_root), key=lambda x: os.path.getmtime(os.path.join(plog_root, x)), reverse=True):
            full = os.path.join(plog_root, d)
            if not os.path.isdir(full):
                continue
            if d.replace('_', '').lower().startswith(norm_prefix):
                return full
    except Exception:
        return None
    return None


class TriggerLogger:
    def __init__(self, participant_token, scenario_label, plog_root=None):
        self.participant_token = participant_token
        self.scenario_label = scenario_label
        if plog_root is None:
            plog_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '_plog'))
        self.plog_root = plog_root
        self.participant_dir = _find_participant_dir_for_events(participant_token)

    def log_trigger(self, trigger_id, trigger_type, activated_at=None, window_duration_seconds=None):
        if self.participant_dir is None:
            print(f"[TriggerLogger] participant dir not found for token '{self.participant_token}' (searched under {self.plog_root})")
            return False
        sname = self.scenario_label
        filename = os.path.join(self.participant_dir, f"{sname}_trigger_log.json")
        entry = {
            'trigger_id': trigger_id,
            'trigger_type': trigger_type,
            'activated_at': activated_at or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'window_duration_seconds': float(window_duration_seconds) if window_duration_seconds is not None else None,
        }
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as fh:
                    try:
                        data = json.load(fh)
                        if not isinstance(data, list):
                            data = []
                    except Exception:
                        data = []
            else:
                data = []
            data.append(entry)
            temp = f"{filename}.tmp"
            with open(temp, 'w', encoding='utf-8') as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
                fh.flush(); os.fsync(fh.fileno())
            os.replace(temp, filename)
            print(f"[TriggerLogger] Appended trigger {trigger_id} -> {filename}")
            return True
        except Exception as e:
            print(f"[TriggerLogger] Failed to append trigger: {e}")
            return False