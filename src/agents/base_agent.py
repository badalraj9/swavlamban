import time
import logging
from enum import Enum
from src.utils.message import Message
import statistics

class AgentState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class BaseAgent:
    def __init__(self, agent_id: int, incoming_queue, outgoing_queue):
        self.agent_id = agent_id
        self.incoming_queue = incoming_queue
        self.outgoing_queue = outgoing_queue
        self.state = AgentState.FOLLOWER
        self.leader_id = None
        self.running = True
        self.logger = logging.getLogger(f"Agent-{self.agent_id}")
        logging.basicConfig(level=logging.INFO)

        self.cycle_times = []

    def run(self):
        """Main loop."""
        while self.running:
            start_time = time.time()
            self.process_incoming_messages()
            self.update_state()
            self.execute_tasks()

            # Record cycle time
            elapsed = time.time() - start_time
            self.cycle_times.append(elapsed)

            # Log metrics every 100 cycles
            if len(self.cycle_times) >= 100:
                p99 = statistics.quantiles(self.cycle_times, n=100)[98] # 99th percentile
                self.logger.info(f"PERF: P99={p99*1000:.2f}ms Max={max(self.cycle_times)*1000:.2f}ms")
                self.cycle_times = []

            # 10Hz throttle
            # We already measured elapsed, so sleep remainder
            sleep_time = max(0, 0.1 - elapsed)
            time.sleep(sleep_time)

    def process_incoming_messages(self):
        while not self.incoming_queue.empty():
            try:
                msg_json = self.incoming_queue.get_nowait()
                msg = Message.from_json(msg_json)
                self.handle_message(msg)
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    def handle_message(self, msg: Message):
        """Override in subclasses."""
        pass

    def send_message(self, receiver_id: int, msg_type: str, content: dict):
        msg = Message(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            msg_type=msg_type,
            content=content
        )
        self.outgoing_queue.put(msg.to_json())

    def update_state(self):
        """State machine logic."""
        pass

    def execute_tasks(self):
        """Task execution logic."""
        pass

    def stop(self):
        self.running = False
