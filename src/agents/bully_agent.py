from src.agents.base_agent import BaseAgent, AgentState
from src.utils.message import Message
import time
import uuid

class BullyAgent(BaseAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue):
        super().__init__(agent_id, incoming_queue, outgoing_queue)
        self.leader_id = None
        self.coordinator_timeout = 2.0
        self.election_timeout = 1.0
        self.last_leader_msg = time.time()
        self.election_start_time = 0.0
        self.waiting_for_answer = False

        # Identity Binding & Term
        self.boot_uuid = uuid.uuid4().hex[:8]
        self.term = 0
        self.known_leaders = {} # id -> {"uuid": uuid, "last_claim": time, "term": term}

    def update_state(self):
        current_time = time.time()

        # Check leader timeout
        if self.state == AgentState.FOLLOWER:
            if current_time - self.last_leader_msg > self.coordinator_timeout:
                self.logger.info(f"Leader timed out. Starting election.")
                self.start_election()

        elif self.state == AgentState.CANDIDATE:
            if self.waiting_for_answer:
                if current_time - self.election_start_time > self.election_timeout:
                    self.declare_victory()

        elif self.state == AgentState.LEADER:
            if getattr(self, 'last_broadcast', 0) == 0 or current_time - self.last_broadcast > 0.5:
                # Include Identity & Term
                content = {
                    "id": self.agent_id,
                    "uuid": self.boot_uuid,
                    "term": self.term
                }
                self.send_message(-1, "COORDINATOR", content)
                self.last_broadcast = current_time

    def start_election(self):
        self.state = AgentState.CANDIDATE
        self.election_start_time = time.time()
        self.waiting_for_answer = True
        self.leader_id = None

        self.term += 1 # New election term
        content = {
            "id": self.agent_id,
            "uuid": self.boot_uuid,
            "term": self.term
        }
        self.send_message(-1, "ELECTION", content)

    def declare_victory(self):
        self.state = AgentState.LEADER
        self.leader_id = self.agent_id
        self.waiting_for_answer = False
        self.logger.info(f"Declaring victory. I am the leader.")

        self.term += 1 # Victory starts new term
        content = {
            "id": self.agent_id,
            "uuid": self.boot_uuid,
            "term": self.term
        }
        self.send_message(-1, "COORDINATOR", content)

    def handle_message(self, msg: Message):
        if msg.msg_type in ["ELECTION", "ANSWER", "COORDINATOR"]:
            if "id" not in msg.content:
                sender_id = msg.sender_id
            else:
                sender_id = msg.content["id"]

            # Identity & Rate Check
            msg_uuid = msg.content.get("uuid")
            msg_term = msg.content.get("term", 0)

            if msg.msg_type == "COORDINATOR":
                # Rate Limiting: Max 1 claim per 0.2s
                current_time = time.time()
                if sender_id in self.known_leaders:
                    record = self.known_leaders[sender_id]

                    # 1. Term Check (Stale Leader)
                    # Reject only if strictly LESS than known (and UUID matches)
                    # If Term is HIGHER, it implies new election/state, so we accept (and update UUID if needed)
                    # But we must verify UUID consistency if term is same or less?

                    # Improved Logic:
                    # If msg_term > record["term"]: Accept (New Term) -> Updates record
                    # If msg_term < record["term"]: Reject (Stale)
                    # If msg_term == record["term"]: Check UUID & Rate

                    if msg_term > record["term"]:
                        # Accept new term (allows reboot or new election to supersede)
                        pass
                    elif msg_term < record["term"]:
                        self.logger.warning(f"SECURITY: Stale term {msg_term} < {record['term']} from {sender_id}. Ignoring.")
                        return
                    else:
                        # Terms equal: Check UUID and Rate
                        if record["uuid"] and msg_uuid and record["uuid"] != msg_uuid:
                            self.logger.warning(f"SECURITY: UUID mismatch for Agent {sender_id}. Ignoring.")
                            return

                        if current_time - record["last_claim"] < 0.2:
                             self.logger.warning(f"SECURITY: Rate limit exceeded for Agent {sender_id}. Ignoring.")
                             return

                # Update Record
                self.known_leaders[sender_id] = {
                    "uuid": msg_uuid,
                    "last_claim": current_time,
                    "term": msg_term
                }

            if msg.msg_type == "ELECTION":
                if self.agent_id > sender_id:
                    self.send_message(sender_id, "ANSWER", {
                        "id": self.agent_id,
                        "uuid": self.boot_uuid,
                        "term": self.term
                    })
                    if self.state != AgentState.LEADER and self.state != AgentState.CANDIDATE:
                        self.start_election()

            elif msg.msg_type == "ANSWER":
                if self.state == AgentState.CANDIDATE and sender_id > self.agent_id:
                    self.waiting_for_answer = False
                    self.state = AgentState.FOLLOWER
                    self.last_leader_msg = time.time()

            elif msg.msg_type == "COORDINATOR":
                # Only accept if passed validation above
                if sender_id > self.agent_id or (self.leader_id is None) or (sender_id == self.leader_id):
                    self.state = AgentState.FOLLOWER
                    self.leader_id = sender_id
                    self.last_leader_msg = time.time()
                    self.waiting_for_answer = False
                elif sender_id < self.agent_id:
                    if self.state == AgentState.LEADER:
                         self.send_message(sender_id, "COORDINATOR", {
                             "id": self.agent_id,
                             "uuid": self.boot_uuid,
                             "term": self.term
                        })
                    else:
                        self.start_election()
