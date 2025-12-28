import multiprocessing
import time
import logging
import random
import json
from src.utils.message import Message

class Simulator:
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.queues = {} # agent_id -> (incoming_queue, outgoing_queue)
        self.processes = []
        self.running = False
        self.logger = logging.getLogger("Simulator")
        # logging.basicConfig(level=logging.INFO)

        # Central switchboard
        self.switchboard_queue = multiprocessing.Queue()

    def setup_agents(self, AgentClass):
        for i in range(self.num_agents):
            incoming = multiprocessing.Queue()
            self.queues[i] = incoming

            p = multiprocessing.Process(
                target=self._run_agent,
                args=(AgentClass, i, incoming, self.switchboard_queue)
            )
            self.processes.append(p)

    def _run_agent(self, AgentClass, agent_id, incoming, outgoing):
        agent = AgentClass(agent_id, incoming, outgoing)
        try:
            agent.run()
        except KeyboardInterrupt:
            pass

    def start_async(self):
        self.running = True
        for p in self.processes:
            p.start()

    def stop(self):
        self.running = False
        for p in self.processes:
            if p.is_alive():
                p.terminate()
        for p in self.processes:
            p.join()

    def step(self, duration: float):
        """Runs the switchboard for a duration."""
        start_time = time.time()
        while time.time() - start_time < duration:
            # Process network
            while not self.switchboard_queue.empty():
                try:
                    msg_json = self.switchboard_queue.get_nowait()
                    msg = Message.from_json(msg_json)
                    self._deliver_message(msg)
                except Exception:
                    pass
            time.sleep(0.01)

    def kill_agent(self, agent_id):
        if 0 <= agent_id < len(self.processes):
            p = self.processes[agent_id]
            if p.is_alive():
                p.terminate()
                p.join()
                self.logger.info(f"Killed Agent {agent_id}")

    def _deliver_message(self, msg: Message):
        if msg.receiver_id == -1: # Broadcast
            for aid, q in self.queues.items():
                if aid != msg.sender_id:
                    # Check if process is alive before queuing?
                    # For now just queue, dead agent won't read.
                    q.put(msg.to_json())
        elif msg.receiver_id in self.queues:
            self.queues[msg.receiver_id].put(msg.to_json())
