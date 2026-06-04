#!/usr/bin/env python

import argparse
import os
import random
import sys
import time

import carla

try:
    from events_scenario02_static_props import get_static_prop_spawns
except ModuleNotFoundError:
    from scenario_events.events_scenario02_static_props import get_static_prop_spawns


START_TO_TRASH_DELAY = 1.0
TRASH_TO_UNCIVBEHAV_DELAY = 1.0
UNCIVBEHAV_TO_POORROAD_DELAY = 5.0
POORROAD_TO_SMELL_DELAY = 2.0
SMELL_TO_DRIVERTRASH_DELAY = 1.0
DRIVERTRASH_TO_SNAKE_DELAY = 1.0
SNAKE_TO_END_DELAY = 1.0

SIM_STEP_S = 0.05
run_in_singleFile_mode = True
DEBUG_MODE = True

TRIGGER_TRASH = True
TRIGGER_UNCIVBEHAV = True
TRIGGER_POORROAD = True
TRIGGER_SMELL = True
TRIGGER_DRIVERTRASH = True
TRIGGER_SNAKE = True

class Scenario02Runner:
    def __init__(self, host, port, tm_port, done_file=None, trigger_trash=True, trigger_uncivbehav=True,
                 trigger_poorroad=True, trigger_smell=True, trigger_drivertrash=True, trigger_snake=True):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        self.host = host
        self.port = port
        self._tm_port = tm_port
        self._done_file = done_file
        self._rng = random.Random()

        self._trigger_trash = trigger_trash
        self._trigger_uncivbehav = trigger_uncivbehav
        self._trigger_poorroad = trigger_poorroad
        self._trigger_smell = trigger_smell
        self._trigger_drivertrash = trigger_drivertrash
        self._trigger_snake = trigger_snake

        self._start_sim_time = None
        self._scenario_done = False

        self.trash_finished = False
        self.uncivbehav_finished = False
        self.poorroad_finished = False
        self.smell_finished = False
        self.drivertrash_finished = False
        self.snake_finished = False

        self._delay_states = {
            "start_to_trash": {
                "delay": START_TO_TRASH_DELAY,
                "started_at": None,
                "finished": False,
            },
            "trash_to_uncivbehav": {
                "delay": TRASH_TO_UNCIVBEHAV_DELAY,
                "started_at": None,
                "finished": False,
            },
            "uncivbehav_to_poorroad": {
                "delay": UNCIVBEHAV_TO_POORROAD_DELAY,
                "started_at": None,
                "finished": False,
            },
            "poorroad_to_smell": {
                "delay": POORROAD_TO_SMELL_DELAY,
                "started_at": None,
                "finished": False,
            },
            "smell_to_drivertrash": {
                "delay": SMELL_TO_DRIVERTRASH_DELAY,
                "started_at": None,
                "finished": False,
            },
            "drivertrash_to_snake": {
                "delay": DRIVERTRASH_TO_SNAKE_DELAY,
                "started_at": None,
                "finished": False,
            },
            "snake_to_end": {
                "delay": SNAKE_TO_END_DELAY,
                "started_at": None,
                "finished": False,
            },
        }

    def _start_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return
        if delay_state["started_at"] is None:
            print(f"[{delay_name}] delay started!")
        delay_state["started_at"] = sim_time
        delay_state["finished"] = False

    def _finish_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None:
            return
        if delay_state["started_at"] is None:
            print(f"[{delay_name}] delay started!")
            delay_state["started_at"] = sim_time
        delay_state["finished"] = True

    def _update_delay_timer(self, delay_name, sim_time):
        delay_state = self._delay_states.get(delay_name)
        if delay_state is None or delay_state["finished"]:
            return
        if delay_state["started_at"] is None:
            delay_state["started_at"] = sim_time
            return
        if (sim_time - delay_state["started_at"]) >= delay_state["delay"]:
            delay_state["finished"] = True
            print(f"[{delay_name}] delay finished!")

    def _update_trash_trigger(self):
        delay_state = self._delay_states.get("start_to_trash")
        return delay_state is not None and delay_state["finished"]

    def _update_uncivbehav_trigger(self):
        delay_state = self._delay_states.get("trash_to_uncivbehav")
        return delay_state is not None and delay_state["finished"]

    def _update_poorroad_trigger(self):
        delay_state = self._delay_states.get("uncivbehav_to_poorroad")
        return delay_state is not None and delay_state["finished"]

    def _update_smell_trigger(self):
        delay_state = self._delay_states.get("poorroad_to_smell")
        return delay_state is not None and delay_state["finished"]

    def _update_drivertrash_trigger(self):
        delay_state = self._delay_states.get("smell_to_drivertrash")
        return delay_state is not None and delay_state["finished"]

    def _update_snake_trigger(self):
        delay_state = self._delay_states.get("drivertrash_to_snake")
        return delay_state is not None and delay_state["finished"]

    def find_hero(self):
        for actor in self.world.get_actors():
            if actor.attributes.get("role_name") in ["hero", "default_player"]:
                return actor
        return None

    def start_trash(self):
        if self.trash_finished:
            return
        print("[Scenario02] start_trash()")
        self.trash_finished = True

    def start_uncivbehav(self):
        if self.uncivbehav_finished:
            return
        print("[Scenario02] start_uncivbehav()")
        self.uncivbehav_finished = True

    def start_poorroad(self):
        if self.poorroad_finished:
            return
        print("[Scenario02] start_poorroad()")
        self.poorroad_finished = True

    def start_smell(self):
        if self.smell_finished:
            return
        print("[Scenario02] start_smell()")
        self.smell_finished = True

    def start_drivertrash(self):
        if self.drivertrash_finished:
            return
        print("[Scenario02] start_drivertrash()")
        self.drivertrash_finished = True

    def start_snake(self):
        if self.snake_finished:
            return
        print("[Scenario02] start_snake()")
        self.snake_finished = True

    def _skip_trash_trigger(self, sim_time):
        if self.trash_finished:
            return
        self._finish_delay_timer("start_to_trash", sim_time)
        self.start_trash()
        print("[Scenario02] Trash trigger skipped.")

    def _skip_uncivbehav_trigger(self, sim_time):
        if self.uncivbehav_finished:
            return
        self._finish_delay_timer("trash_to_uncivbehav", sim_time)
        self.start_uncivbehav()
        print("[Scenario02] UncivBehav trigger skipped.")

    def _skip_poorroad_trigger(self, sim_time):
        if self.poorroad_finished:
            return
        self._finish_delay_timer("uncivbehav_to_poorroad", sim_time)
        self.start_poorroad()
        print("[Scenario02] PoorRoad trigger skipped.")

    def _skip_smell_trigger(self, sim_time):
        if self.smell_finished:
            return
        self._finish_delay_timer("poorroad_to_smell", sim_time)
        self.start_smell()
        print("[Scenario02] Smell trigger skipped.")

    def _skip_drivertrash_trigger(self, sim_time):
        if self.drivertrash_finished:
            return
        self._finish_delay_timer("smell_to_drivertrash", sim_time)
        self.start_drivertrash()
        print("[Scenario02] DriverTrash trigger skipped.")

    def _skip_snake_trigger(self, sim_time):
        if self.snake_finished:
            return
        self._finish_delay_timer("drivertrash_to_snake", sim_time)
        self.start_snake()
        print("[Scenario02] Snake trigger skipped.")

    def destroy(self):
        pass

    def _signal_done(self):
        if not self._done_file:
            return
        try:
            done_dir = os.path.dirname(self._done_file)
            if done_dir:
                os.makedirs(done_dir, exist_ok=True)
            with open(self._done_file, "w", encoding="utf-8") as done_handle:
                done_handle.write("done\n")
        except Exception as exc:
            print(f"[Scenario02] WARNING: could not write done signal file: {exc}")

    def run(self):
        print("[Scenario02] Running...")
        if run_in_singleFile_mode:
            print("[Scenario02] Running in single-file mode")

        try:
            while True:
                self.world.wait_for_tick()
                sim_time = self.world.get_snapshot().timestamp.elapsed_seconds

                if self._start_sim_time is None:
                    self._start_sim_time = sim_time

                start_to_trash_state = self._delay_states["start_to_trash"]
                if start_to_trash_state["started_at"] is None:
                    self._start_delay_timer("start_to_trash", sim_time)
                self._update_delay_timer("start_to_trash", sim_time)

                if self._update_trash_trigger() and not self.trash_finished:
                    if not self._trigger_trash:
                        self._skip_trash_trigger(sim_time)
                    else:
                        self.start_trash()

                trash_to_uncivbehav_state = self._delay_states["trash_to_uncivbehav"]
                if self.trash_finished:
                    if trash_to_uncivbehav_state["started_at"] is None:
                        self._start_delay_timer("trash_to_uncivbehav", sim_time)
                    self._update_delay_timer("trash_to_uncivbehav", sim_time)

                if self.trash_finished and trash_to_uncivbehav_state["finished"] and not self.uncivbehav_finished:
                    if not self._trigger_uncivbehav:
                        self._skip_uncivbehav_trigger(sim_time)
                    else:
                        self.start_uncivbehav()

                uncivbehav_to_poorroad_state = self._delay_states["uncivbehav_to_poorroad"]
                if self.uncivbehav_finished:
                    if uncivbehav_to_poorroad_state["started_at"] is None:
                        self._start_delay_timer("uncivbehav_to_poorroad", sim_time)
                    self._update_delay_timer("uncivbehav_to_poorroad", sim_time)

                if self.uncivbehav_finished and uncivbehav_to_poorroad_state["finished"] and not self.poorroad_finished:
                    if not self._trigger_poorroad:
                        self._skip_poorroad_trigger(sim_time)
                    else:
                        self.start_poorroad()

                poorroad_to_smell_state = self._delay_states["poorroad_to_smell"]
                if self.poorroad_finished:
                    if poorroad_to_smell_state["started_at"] is None:
                        self._start_delay_timer("poorroad_to_smell", sim_time)
                    self._update_delay_timer("poorroad_to_smell", sim_time)

                if self.poorroad_finished and poorroad_to_smell_state["finished"] and not self.smell_finished:
                    if not self._trigger_smell:
                        self._skip_smell_trigger(sim_time)
                    else:
                        self.start_smell()

                smell_to_drivertrash_state = self._delay_states["smell_to_drivertrash"]
                if self.smell_finished:
                    if smell_to_drivertrash_state["started_at"] is None:
                        self._start_delay_timer("smell_to_drivertrash", sim_time)
                    self._update_delay_timer("smell_to_drivertrash", sim_time)

                if self.smell_finished and smell_to_drivertrash_state["finished"] and not self.drivertrash_finished:
                    if not self._trigger_drivertrash:
                        self._skip_drivertrash_trigger(sim_time)
                    else:
                        self.start_drivertrash()

                drivertrash_to_snake_state = self._delay_states["drivertrash_to_snake"]
                if self.drivertrash_finished:
                    if drivertrash_to_snake_state["started_at"] is None:
                        self._start_delay_timer("drivertrash_to_snake", sim_time)
                    self._update_delay_timer("drivertrash_to_snake", sim_time)

                if self.drivertrash_finished and drivertrash_to_snake_state["finished"] and not self.snake_finished:
                    if not self._trigger_snake:
                        self._skip_snake_trigger(sim_time)
                    else:
                        self.start_snake()

                snake_to_end_state = self._delay_states["snake_to_end"]
                if self.snake_finished:
                    if snake_to_end_state["started_at"] is None:
                        self._start_delay_timer("snake_to_end", sim_time)
                    self._update_delay_timer("snake_to_end", sim_time)

                if self.snake_finished and snake_to_end_state["finished"]:
                    self._scenario_done = True

                if self._scenario_done:
                    return

                time.sleep(SIM_STEP_S)
        except KeyboardInterrupt:
            pass
        finally:
            self.destroy()
            self._signal_done()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=2000, type=int)
    parser.add_argument("--tm-port", default=8000, type=int)
    parser.add_argument("--done-file", default=None)
    args = parser.parse_args()

    Scenario02Runner(
        args.host,
        args.port,
        args.tm_port,
        args.done_file,
        trigger_trash=TRIGGER_TRASH,
        trigger_uncivbehav=TRIGGER_UNCIVBEHAV,
        trigger_poorroad=TRIGGER_POORROAD,
        trigger_smell=TRIGGER_SMELL,
        trigger_drivertrash=TRIGGER_DRIVERTRASH,
        trigger_snake=TRIGGER_SNAKE,
    ).run()
