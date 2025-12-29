import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import time
import os
import argparse

# Configuration
LOG_FILE = "hell_test.log"
NUM_AGENTS = 10

# Regex Patterns
RE_AGENT_LOG = re.compile(r"Agent-(\d+)")
RE_LEADER_VICTORY = re.compile(r"Declaring victory. I am the leader")
RE_DEGRADED = re.compile(r"ENTERING DEGRADED OPERATIONS MODE")
RE_NORMAL = re.compile(r"RETURNING TO NORMAL OPERATIONS MODE")
RE_KILLED = re.compile(r"Killed Agent (\d+)")

# State
agent_states = {i: "FOLLOWER" for i in range(NUM_AGENTS)} # FOLLOWER, LEADER, DEAD
system_mode = "NORMAL" # NORMAL, DEGRADED
log_lines_buffer = []

def parse_line(line):
    global system_mode

    # Check System Mode
    if RE_DEGRADED.search(line):
        system_mode = "DEGRADED"
        return
    if RE_NORMAL.search(line):
        system_mode = "NORMAL"
        return

    # Check Kill
    kill_match = RE_KILLED.search(line)
    if kill_match:
        aid = int(kill_match.group(1))
        agent_states[aid] = "DEAD"
        return

    # Check Agent Activity
    agent_match = RE_AGENT_LOG.search(line)
    if agent_match:
        aid = int(agent_match.group(1))

        # If agent speaks, it's alive (resurrection check)
        if agent_states[aid] == "DEAD":
             agent_states[aid] = "FOLLOWER"

        if RE_LEADER_VICTORY.search(line):
            # Reset others to follower? Ideally yes, but let's just mark this one
            # The backend makes others followers. We can't easily see that in logs
            # without parsing "FOLLOWER" transitions which aren't explicitly logged in standard flow.
            # Visual hack: Make this one leader, others followers (unless dead)
            for i in range(NUM_AGENTS):
                if agent_states[i] == "LEADER":
                    agent_states[i] = "FOLLOWER"
            agent_states[aid] = "LEADER"

def update(frame):
    # Read new lines
    global file_handle
    where = file_handle.tell()
    line = file_handle.readline()
    while line:
        parse_line(line)
        log_lines_buffer.append(line.strip())
        if len(log_lines_buffer) > 5:
            log_lines_buffer.pop(0)
        line = file_handle.readline()

    # Clear and Redraw
    ax.clear()

    # Background Color based on Mode
    if system_mode == "DEGRADED":
        ax.set_facecolor('#fff3cd') # Yellowish warning
        ax.set_title(f"SWARM STATUS: DEGRADED (MISSION CONTINUITY MODE)", color='red', weight='bold')
    else:
        ax.set_facecolor('white')
        ax.set_title(f"SWARM STATUS: NORMAL", color='green', weight='bold')

    # Draw Agents
    # Layout: Circle
    import math
    radius = 10

    for i in range(NUM_AGENTS):
        angle = 2 * math.pi * i / NUM_AGENTS
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        state = agent_states[i]

        if state == "LEADER":
            color = 'red'
            size = 300
            marker = '*'
        elif state == "DEAD":
            color = 'gray'
            size = 100
            marker = 'x'
        else: # FOLLOWER
            color = 'blue'
            size = 100
            marker = 'o'

        ax.scatter(x, y, c=color, s=size, marker=marker)
        ax.text(x, y+1.5, f"A{i}", ha='center')

    # Connectivity Lines (Mesh)
    # Draw faint lines between alive agents
    alive_agents = [i for i, s in agent_states.items() if s != "DEAD"]
    for i in range(len(alive_agents)):
        for j in range(i+1, len(alive_agents)):
            a1 = alive_agents[i]
            a2 = alive_agents[j]
            angle1 = 2 * math.pi * a1 / NUM_AGENTS
            angle2 = 2 * math.pi * a2 / NUM_AGENTS
            x1, y1 = radius * math.cos(angle1), radius * math.sin(angle1)
            x2, y2 = radius * math.cos(angle2), radius * math.sin(angle2)
            ax.plot([x1, x2], [y1, y2], color='gray', alpha=0.1)

    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 15)
    ax.axis('off')

    # Text Log
    log_text = "\n".join(log_lines_buffer)
    ax.text(0, -14, log_text, ha='center', fontsize=8, family='monospace')

# Setup
fig, ax = plt.subplots(figsize=(8, 8))
file_handle = None

def main():
    global file_handle

    # Ensure log file exists or wait for it
    print(f"Waiting for {LOG_FILE}...")
    while not os.path.exists(LOG_FILE):
        time.sleep(1)

    file_handle = open(LOG_FILE, 'r')

    ani = animation.FuncAnimation(fig, update, interval=100) # 10Hz update
    plt.show()

if __name__ == "__main__":
    main()
