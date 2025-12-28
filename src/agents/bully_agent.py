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

        # We need to know who are the peers to send Election messages to higher IDs
        # In a dynamic system, we'd discover them. Here, we assume we know IDs 0..N-1
        # Ideally this is passed in config, but for now we'll assume a max_id or just broadcast
        # and ignore replies from lower IDs.

    def update_state(self):
        current_time = time.time()

        # Check leader timeout
        if self.state == AgentState.FOLLOWER:
            if current_time - self.last_leader_msg > self.coordinator_timeout:
                self.logger.info(f"Leader timed out. Starting election.")
                self.start_election()

        elif self.state == AgentState.CANDIDATE:
            # If I started election and haven't heard back (Answer) within timeout
            if self.waiting_for_answer:
                if current_time - self.election_start_time > self.election_timeout:
                    # No one higher responded. I win.
                    self.declare_victory()

        elif self.state == AgentState.LEADER:
            # Send periodic Coordinator/Heartbeat
            if getattr(self, 'last_broadcast', 0) == 0 or current_time - self.last_broadcast > 0.5:
                self.send_message(-1, "COORDINATOR", {"id": self.agent_id})
                self.last_broadcast = current_time

    def start_election(self):
        self.state = AgentState.CANDIDATE
        self.election_start_time = time.time()
        self.waiting_for_answer = True
        self.leader_id = None

        # Send ELECTION to all higher IDs
        # Since we might not know exactly who exists, we broadcast "ELECTION".
        # Receivers with higher ID will respond "ANSWER".
        # Receivers with lower ID will ignore.
        self.send_message(-1, "ELECTION", {"id": self.agent_id})

    def declare_victory(self):
        self.state = AgentState.LEADER
        self.leader_id = self.agent_id
        self.waiting_for_answer = False
        self.logger.info(f"Declaring victory. I am the leader.")
        self.send_message(-1, "COORDINATOR", {"id": self.agent_id})

    def handle_message(self, msg: Message):
        sender_id = msg.content["id"]

        if msg.msg_type == "ELECTION":
            if self.agent_id > sender_id:
                # I am higher, so I take over
                self.send_message(sender_id, "ANSWER", {"id": self.agent_id})
                # And I start my own election if I'm not already leader
                if self.state != AgentState.LEADER and self.state != AgentState.CANDIDATE:
                    self.start_election()

        elif msg.msg_type == "ANSWER":
            if self.state == AgentState.CANDIDATE and sender_id > self.agent_id:
                # Someone higher is alive, I wait for them to become leader
                self.waiting_for_answer = False
                self.state = AgentState.FOLLOWER
                self.last_leader_msg = time.time() # Reset timeout to give them time to finish

        elif msg.msg_type == "COORDINATOR":
            if sender_id > self.agent_id or (self.leader_id is None) or (sender_id == self.leader_id):
                self.state = AgentState.FOLLOWER
                self.leader_id = sender_id
                self.last_leader_msg = time.time()
                self.waiting_for_answer = False
            elif sender_id < self.agent_id:
                # Lower ID claims to be leader? Bully them.
                if self.state == AgentState.LEADER:
                    # I am already leader, re-assert
                    self.send_message(sender_id, "COORDINATOR", {"id": self.agent_id})
                else:
                    self.start_election()
