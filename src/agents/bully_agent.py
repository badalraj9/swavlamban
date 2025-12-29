from src.agents.base_agent import BaseAgent, AgentState
from src.utils.message import Message
import time

class BullyAgent(BaseAgent):
    def __init__(self, agent_id, incoming_queue, outgoing_queue):
        super().__init__(agent_id, incoming_queue, outgoing_queue)
        self.leader_id = None
        self.coordinator_timeout = 2.0
        self.election_timeout = 1.0
        self.last_leader_msg = time.time()
        self.election_start_time = 0.0
        self.waiting_for_answer = False

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
                self.send_message(-1, "COORDINATOR", {"id": self.agent_id})
                self.last_broadcast = current_time

    def start_election(self):
        self.state = AgentState.CANDIDATE
        self.election_start_time = time.time()
        self.waiting_for_answer = True
        self.leader_id = None
        self.send_message(-1, "ELECTION", {"id": self.agent_id})

    def declare_victory(self):
        self.state = AgentState.LEADER
        self.leader_id = self.agent_id
        self.waiting_for_answer = False
        self.logger.info(f"Declaring victory. I am the leader.")
        self.send_message(-1, "COORDINATOR", {"id": self.agent_id})

    def handle_message(self, msg: Message):
        # Fix: Check msg_type first to avoid KeyErrors on foreign messages
        if msg.msg_type in ["ELECTION", "ANSWER", "COORDINATOR"]:
            if "id" not in msg.content:
                # Fallback to sender_id if content missing (though we send it)
                sender_id = msg.sender_id
            else:
                sender_id = msg.content["id"]

            if msg.msg_type == "ELECTION":
                if self.agent_id > sender_id:
                    self.send_message(sender_id, "ANSWER", {"id": self.agent_id})
                    if self.state != AgentState.LEADER and self.state != AgentState.CANDIDATE:
                        self.start_election()

            elif msg.msg_type == "ANSWER":
                if self.state == AgentState.CANDIDATE and sender_id > self.agent_id:
                    self.waiting_for_answer = False
                    self.state = AgentState.FOLLOWER
                    self.last_leader_msg = time.time()

            elif msg.msg_type == "COORDINATOR":
                if sender_id > self.agent_id or (self.leader_id is None) or (sender_id == self.leader_id):
                    self.state = AgentState.FOLLOWER
                    self.leader_id = sender_id
                    self.last_leader_msg = time.time()
                    self.waiting_for_answer = False
                elif sender_id < self.agent_id:
                    if self.state == AgentState.LEADER:
                        self.send_message(sender_id, "COORDINATOR", {"id": self.agent_id})
                    else:
                        self.start_election()
