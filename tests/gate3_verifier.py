import unittest
import time
import multiprocessing
import statistics
from src.simulation.simulator import Simulator
from src.agents.cbaa_agent import CbaaAgent
from src.utils.message import Message

class InstrumentedSimulator(Simulator):
    def __init__(self, num_agents):
        super().__init__(num_agents)
        self.msg_history = []
        self.last_msg_time = 0

    def _deliver_message(self, msg: Message):
        super()._deliver_message(msg)
        self.msg_history.append((time.time(), msg))
        self.last_msg_time = time.time()

def run_gate3_verification():
    print("Running Gate 3 (Resilience / N-1)...")
    sim = InstrumentedSimulator(num_agents=5)
    sim.setup_agents(CbaaAgent)
    sim.start_async()

    # 1. Wait for initial convergence
    print("Waiting for initial convergence...")
    sim.step(3.0)

    # Capture state
    last_z = {}
    for t, msg in sim.msg_history:
        if msg.msg_type == "CBAA_UPDATE":
            last_z[msg.sender_id] = msg.content["z"]

    if not last_z:
        print("No initial convergence?")
        sim.stop()
        return

    initial_assignment = list(last_z.values())[0]
    print(f"Initial Assignment: {initial_assignment}")

    # 2. Identify an agent with tasks and Kill it
    # Find an agent who owns at least one task
    victim_id = -1
    for aid in range(5):
        if initial_assignment.count(aid) > 0:
            victim_id = aid
            break

    if victim_id == -1:
        print("No agent owns any tasks? Odd distribution.")
        victim_id = 0

    print(f"Killing Agent {victim_id}...")
    sim.kill_agent(victim_id)

    # Clear history to track new updates
    sim.msg_history = []

    # 3. Wait for Re-Convergence
    # Agents should detect timeout (2s) and release tasks, then re-bid.
    print("Waiting for re-convergence...")
    start_time = time.time()
    reconverged = False

    # Run for up to 10s
    while time.time() - start_time < 10.0:
        sim.step(0.1)
        # Check if updates have stopped for > 2s (indicating stability)
        if time.time() - sim.last_msg_time > 2.0 and len(sim.msg_history) > 0:
            reconverged = True
            break

    if not reconverged:
        print("Did not stabilize after kill.")
        # Check logs?

    # 4. Verify new state
    final_z = {}
    for t, msg in sim.msg_history:
        if msg.msg_type == "CBAA_UPDATE":
            final_z[msg.sender_id] = msg.content["z"]

    sim.stop()

    if not final_z:
        print("No updates after kill? Agents might not have detected death.")
        print("GATE 3 FAILED")
        return

    # Check consistency
    reference = list(final_z.values())[0]
    consistent = all(z == reference for z in final_z.values())

    print(f"Final Assignment: {reference}")

    # Verify victim owns nothing
    if victim_id in reference:
        print(f"FAIL: Dead Agent {victim_id} still owns tasks in {reference}")
        print("GATE 3 FAILED")
    elif consistent:
        print("State Consistent and Dead Agent removed.")
        print("GATE 3 PASSED")
    else:
        print("State Inconsistent")
        print(final_z)
        print("GATE 3 FAILED")

if __name__ == "__main__":
    run_gate3_verification()
