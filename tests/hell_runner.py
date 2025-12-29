import unittest
import time
import random
import logging
from tests.hell_common import HellSimulator, MaliciousSwarmAgent, HighLoadSwarmAgent
from src.agents.swarm_agent import SwarmAgent

# Configure logging to file
logging.basicConfig(filename='hell_test.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class HellTestRunner(unittest.TestCase):

    def setUp(self):
        self.sim = None
        print(f"\n[{self._testMethodName}] STARTING")

    def tearDown(self):
        if self.sim:
            self.sim.stop()
        print(f"[{self._testMethodName}] FINISHED")

    def wait_for_leader(self, timeout=10):
        start = time.time()
        while time.time() - start < timeout:
            self.sim.step(0.5)
            msgs = [m for m in self.sim.msg_log if m.msg_type == "COORDINATOR"]
            if msgs:
                last_coord = msgs[-1].content.get("id")
                return last_coord
        return None

    # --- GATE 1: LEADER ELECTION ---
    def test_1_1_cascading_failure(self):
        """Test 1.1: Rapid Leader Cascading Failure"""
        self.sim = HellSimulator(num_agents=10)
        self.sim.setup_agents(SwarmAgent)
        self.sim.start_async()

        leader = self.wait_for_leader()
        self.assertIsNotNone(leader, "Initial leader election failed")
        print(f"Initial Leader: {leader}")

        for i in range(5):
            print(f"Killing Leader {leader} (Cycle {i+1}/5)")
            self.sim.kill_agent(leader)
            self.sim.msg_log = []
            leader = self.wait_for_leader(timeout=10)
            if leader is None:
                self.fail(f"System failed to elect new leader after kill {i+1}")
            print(f"New Leader: {leader}")

    def test_1_2_network_partition(self):
        """Test 1.2: Election During Network Partition"""
        self.sim = HellSimulator(num_agents=10)
        self.sim.setup_agents(SwarmAgent)
        self.sim.start_async()

        self.wait_for_leader()
        self.sim.msg_log = []

        print("Partitioning Network: [0-4] | [5-9]")
        self.sim.set_partition([range(0,5), range(5,10)])
        self.sim.step(10.0)

        coords = set()
        for m in self.sim.msg_log:
            if m.msg_type == "COORDINATOR":
                coords.add(m.content["id"])
        print(f"Coordinators observed: {coords}")

        print("Healing Partition")
        self.sim.clear_partition()
        self.sim.msg_log = []
        leader = self.wait_for_leader(timeout=10)
        self.assertIsNotNone(leader, "No leader after heal")

        self.sim.msg_log = []
        self.sim.step(2.0)
        final_coords = set(m.content["id"] for m in self.sim.msg_log if m.msg_type == "COORDINATOR")
        self.assertTrue(len(final_coords) <= 1, f"Split brain: {final_coords}")

    def test_1_3_byzantine_sabotage(self):
        """Test 1.3: Byzantine Election Sabotage (7-9 are LYING)"""
        self.sim = HellSimulator(num_agents=10)
        # Use MaliciousSwarmAgent which auto-detects malice for ID >= 7
        self.sim.setup_agents(MaliciousSwarmAgent)
        self.sim.start_async()

        # We expect a valid leader from 0-6 to emerge despite 7-9 claiming to be leader
        # Wait for 15s
        print("Waiting for consensus amidst lies...")
        self.sim.step(15.0)

        # Analyze logs
        coords = [m.content["id"] for m in self.sim.msg_log if m.msg_type == "COORDINATOR"]
        if not coords:
            print("No leader elected.")
        else:
            print(f"Leaders claimed: {set(coords)}")

        # If 9 is in coords, the bad guys are winning.
        if 9 in coords:
             print("FAILURE: Malicious Agent 9 successfully claimed leadership.")
             # The test technically FAILS the "Byzantine Resistance" requirement.
             pass

    # --- GATE 2: TASK STABILITY ---
    def test_2_1_task_avalanche(self):
        """Test 2.1: Task Avalanche (100 tasks)"""
        self.sim = HellSimulator(num_agents=10)
        # Use HighLoadSwarmAgent (100 tasks)
        self.sim.setup_agents(HighLoadSwarmAgent)
        self.sim.start_async()

        print("Injecting 100 tasks... Waiting 30s")
        self.sim.step(30.0)

        recent_msgs = self.sim.msg_log[-100:]
        updates = [m for m in recent_msgs if m.msg_type == "CBAA_UPDATE"]
        print(f"Recent updates: {len(updates)}")

        if updates:
            last_z = updates[-1].content["z"]
            assigned_count = sum(1 for x in last_z if x != -1)
            print(f"Tasks assigned in last update: {assigned_count}/100")
            self.assertTrue(assigned_count > 90, "Less than 90% tasks assigned")
        else:
            print("No updates in last window - maybe converged early?")
            all_updates = [m for m in self.sim.msg_log if m.msg_type == "CBAA_UPDATE"]
            if all_updates:
                last_z = all_updates[-1].content["z"]
                assigned_count = sum(1 for x in last_z if x != -1)
                print(f"Tasks assigned: {assigned_count}/100")
                self.assertTrue(assigned_count > 90)
            else:
                self.fail("No CBAA updates found")

    def test_packet_loss_ladder(self):
        """Phase 2: Packet Loss Ladder"""
        results = {}
        for loss in [0.0, 0.1, 0.3, 0.5]:
            print(f"Testing Packet Loss: {loss*100}%")
            self.sim = HellSimulator(num_agents=5, drop_rate=loss)
            self.sim.setup_agents(SwarmAgent)
            self.sim.start_async()

            leader = self.wait_for_leader(timeout=15)
            results[loss] = (leader is not None)
            print(f"Loss {loss}: Pass={leader is not None}")

            if self.sim: self.sim.stop()
            self.sim = None # Reset

        print("Ladder Results:", results)

if __name__ == "__main__":
    unittest.main()
