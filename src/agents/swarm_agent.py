from src.agents.bully_agent import BullyAgent
from src.agents.cbaa_agent import CbaaAgent
from src.utils.message import Message
import time

# Mock Task Registry for S7
TASK_REGISTRY = {
    i: {"reqs": []} for i in range(100)
}
# Task 5 requires "heavy_lift"
TASK_REGISTRY[5]["reqs"] = ["heavy_lift"]

class SwarmAgent(CbaaAgent, BullyAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue, num_tasks=10, capabilities=None):
        CbaaAgent.__init__(self, agent_id, incoming_queue, outgoing_queue, num_tasks)

        # Bully State Init
        self.leader_id = None
        self.coordinator_timeout = 2.0
        self.election_timeout = 1.0
        self.last_leader_msg = time.time()
        self.election_start_time = 0.0
        self.waiting_for_answer = False

        self.capabilities = capabilities if capabilities else []

    def update_state(self):
        BullyAgent.update_state(self)
        CbaaAgent.update_state(self)

    def handle_message(self, msg: Message):
        BullyAgent.handle_message(self, msg)
        CbaaAgent.handle_message(self, msg)

    def calculate_bid(self, task_id):
        # S7: Capability Check
        reqs = TASK_REGISTRY.get(task_id, {}).get("reqs", [])
        for req in reqs:
            if req not in self.capabilities:
                return 0.0

        return super().calculate_bid(task_id)
