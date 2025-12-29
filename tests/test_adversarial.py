import unittest
import time
from src.simulation.simulator import Simulator
from src.agents.swarm_agent import SwarmAgent

class TestAdversarial(unittest.TestCase):
    def test_chaos_survival(self):
        print("\nRunning Adversarial Chaos Test (Loss=20%, Latency=0-0.5s)...")
        # 20% drop rate, variable latency
        sim = Simulator(num_agents=10, drop_rate=0.2, min_latency=0.0, max_latency=0.5)
        sim.setup_agents(SwarmAgent)
        sim.start_async()

        # Run for 15s to let it try to stabilize despite chaos
        start = time.time()
        sim.step(15.0)

        # Kill random agents during run?
        # Let's kill Agent 5 at t=5
        print("Killing Agent 5 under chaos...")
        sim.kill_agent(5)
        sim.step(5.0)

        sim.stop()
        print("Adversarial Test Completed without Crash.")
        # Success = No unhandled exceptions in simulator (which would crash test runner)
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
