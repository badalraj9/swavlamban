from src.agents.base_agent import BaseAgent, AgentState
from src.utils.message import Message
import time
import random

class CbaaAgent(BaseAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue, num_tasks=10):
        super().__init__(agent_id, incoming_queue, outgoing_queue)
        self.num_tasks = num_tasks

        # State for CBAA
        self.y = [0.0] * num_tasks
        self.z = [-1] * num_tasks

        self.last_change_time = time.time()

        # Neighbor Liveness
        self.neighbor_heartbeats = {} # id -> time
        self.neighbor_timeout = 2.0 # Seconds
        self.last_heartbeat_broadcast = 0.0

    def calculate_bid(self, task_id):
        # Deterministic pseudo-random bid based on agent_id and task_id
        random.seed(self.agent_id * 1000 + task_id)
        return random.random()

    def update_state(self):
        current_time = time.time()

        # 0. Liveness Check
        dead_neighbors = []
        for nid, t in self.neighbor_heartbeats.items():
            if current_time - t > self.neighbor_timeout:
                dead_neighbors.append(nid)

        for nid in dead_neighbors:
            self.logger.info(f"Detected dead neighbor {nid}. Releasing tasks.")
            del self.neighbor_heartbeats[nid]
            # Release tasks owned by dead neighbor
            for j in range(self.num_tasks):
                if self.z[j] == nid:
                    self.y[j] = 0.0
                    self.z[j] = -1
                    # self.last_change_time = current_time # Trigger update

        # 1. Auction Step (Greedy)
        changed = False
        for j in range(self.num_tasks):
            # If task is free or I can beat the bid
            # Note: If I already own it (z[j] == me), I don't need to re-bid unless someone beat me (handled in merge)
            # If I don't own it:
            if self.z[j] != self.agent_id:
                my_bid = self.calculate_bid(j)
                if my_bid > self.y[j]:
                    self.y[j] = my_bid
                    self.z[j] = self.agent_id
                    changed = True

        if changed:
            self.last_change_time = current_time
            self.send_cbaa_update()

        # 2. Heartbeat
        if current_time - self.last_heartbeat_broadcast > 1.0:
            self.send_message(-1, "HEARTBEAT", {})
            self.last_heartbeat_broadcast = current_time

    def send_cbaa_update(self):
        content = {
            "y": self.y,
            "z": self.z
        }
        self.send_message(-1, "CBAA_UPDATE", content)

    def handle_message(self, msg: Message):
        sender_id = msg.sender_id
        self.neighbor_heartbeats[sender_id] = time.time()

        if msg.msg_type == "CBAA_UPDATE":
            neighbor_y = msg.content["y"]
            neighbor_z = msg.content["z"]

            changed = False
            for j in range(self.num_tasks):
                # Max-Consensus Rule
                if neighbor_y[j] > self.y[j]:
                    self.y[j] = neighbor_y[j]
                    self.z[j] = neighbor_z[j]
                    changed = True
                elif neighbor_y[j] == self.y[j]:
                    # Tie-breaking
                    if neighbor_z[j] > self.z[j]:
                        self.z[j] = neighbor_z[j]
                        changed = True

            if changed:
                self.last_change_time = time.time()
                self.send_cbaa_update()

        elif msg.msg_type == "HEARTBEAT":
            # Already updated timestamp above
            pass
