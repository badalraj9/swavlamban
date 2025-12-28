import unittest
import time
import multiprocessing
import statistics
from src.simulation.simulator import Simulator
from src.agents.bully_agent import BullyAgent
from src.utils.message import Message

class InstrumentedSimulator(Simulator):
    def __init__(self, num_agents):
        super().__init__(num_agents)
        self.events = []

    def _deliver_message(self, msg: Message):
        super()._deliver_message(msg)
        if msg.msg_type == "COORDINATOR":
            self.events.append((time.time(), msg))

def run_gate1_verification(trials=50):
    # We will run one long simulation and kill leaders sequentially.
    # When we run out of agents, we restart.

    times = []

    while len(times) < trials:
        sim = InstrumentedSimulator(num_agents=10)
        sim.setup_agents(BullyAgent)
        sim.start_async()

        # Wait for initial stabilization
        sim.step(3.0)

        # We expect Agent 9 to be leader.
        active_agents = list(range(10))
        current_leader = 9

        while len(active_agents) > 1 and len(times) < trials:
            # Clear previous events
            sim.events = []

            # Kill leader
            kill_time = time.time()
            sim.kill_agent(current_leader)
            active_agents.remove(current_leader)

            # Wait for COORDINATOR message from new leader (next highest)
            expected_leader = active_agents[-1]
            found = False

            # Wait loop (max 10s)
            loop_start = time.time()
            while time.time() - loop_start < 10.0:
                sim.step(0.1)
                # Check events
                for t, msg in sim.events:
                    if msg.msg_type == "COORDINATOR" and msg.content["id"] == expected_leader:
                        election_time = t - kill_time
                        times.append(election_time)
                        current_leader = expected_leader
                        found = True
                        break
                if found:
                    break

            if not found:
                print(f"Failed to elect {expected_leader} in time.")
                break

            # Wait a bit for stability
            sim.step(1.0)

        sim.stop()
        print(f"Completed {len(times)}/{trials} trials.")

    # Analyze
    p95 = statistics.quantiles(times, n=20)[18] # 95th percentile
    print(f"Results ({len(times)} trials):")
    print(f"Mean: {statistics.mean(times):.4f}s")
    print(f"95th Percentile: {p95:.4f}s")

    if p95 < 10.0:
        print("GATE 1 PASSED")
    else:
        print("GATE 1 FAILED")
        raise Exception("Gate 1 Failed")

if __name__ == "__main__":
    run_gate1_verification()
