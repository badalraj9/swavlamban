import multiprocessing
import time
import random
import logging
import json
import uuid
from src.simulation.simulator import Simulator
from src.agents.swarm_agent import SwarmAgent
from src.utils.message import Message

class HellSimulator(Simulator):
    def __init__(self, num_agents: int, **kwargs):
        super().__init__(num_agents, **kwargs)
        self.partitions = []
        self.msg_log = []

    def set_partition(self, groups):
        self.partitions = [set(g) for g in groups]

    def clear_partition(self):
        self.partitions = []

    def _deliver_message(self, msg: Message):
        self.msg_log.append(msg)
        if self.partitions:
            sender_group = None
            for idx, group in enumerate(self.partitions):
                if msg.sender_id in group:
                    sender_group = idx
                    break

            if msg.receiver_id == -1:
                for aid, q in self.queues.items():
                    if aid == msg.sender_id:
                        continue
                    receiver_group = None
                    for idx, group in enumerate(self.partitions):
                        if aid in group:
                            receiver_group = idx
                            break
                    if sender_group is not None and sender_group == receiver_group:
                        q.put(msg.to_json())
            else:
                receiver_group = None
                for idx, group in enumerate(self.partitions):
                    if msg.receiver_id in group:
                        receiver_group = idx
                        break
                if sender_group is not None and sender_group == receiver_group:
                     if msg.receiver_id in self.queues:
                        self.queues[msg.receiver_id].put(msg.to_json())
        else:
            super()._deliver_message(msg)

class MaliciousSwarmAgent(SwarmAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue, capabilities=None, malice_mode="NONE"):
        # Auto-detect malice mode
        if malice_mode == "NONE":
            if agent_id >= 7:
                 malice_mode = "LYING_LEADER"

        super().__init__(agent_id, incoming_queue, outgoing_queue, capabilities=capabilities)
        self.malice_mode = malice_mode
        self.start_malice_time = time.time()

        # Malicious agents might use fixed or rotating UUIDs to confuse
        self.fake_uuid = "DEADBEEF"

    def handle_message(self, msg: Message):
        if self.malice_mode == "SILENT":
            return
        super().handle_message(msg)

    def send_message(self, receiver_id: int, msg_type: str, content: dict):
        if self.malice_mode == "SILENT":
            return

        if self.malice_mode == "LYING_LEADER":
            # Sabotage: Claim to be leader with INVALID or STALE credentials
            if msg_type == "ELECTION" or msg_type == "ANSWER":
                msg_type = "COORDINATOR"
                content["id"] = self.agent_id

                # Try 1: Send without UUID/Term (Should fail validation if we were strict, but we just added fields)
                # Try 2: Send with changing UUID (Spoofing)
                content["uuid"] = str(uuid.uuid4())[:8] # Random UUID every time -> Spoofing
                content["term"] = 9999 # Fake high term

        if self.malice_mode == "SPAMMER":
            for _ in range(10):
                super().send_message(receiver_id, msg_type, content)
            return

        super().send_message(receiver_id, msg_type, content)

class HighLoadSwarmAgent(SwarmAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue, capabilities=None):
        super().__init__(agent_id, incoming_queue, outgoing_queue, num_tasks=100, capabilities=capabilities)
