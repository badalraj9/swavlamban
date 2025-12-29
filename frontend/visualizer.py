import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import re
import time
import os
import math

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

# Theme Colors (Hacker Vibe)
COLOR_BG = '#000000'
COLOR_TEXT_NORMAL = '#00FF00' # Matrix Green
COLOR_TEXT_DEGRADED = '#FFB000' # Amber
COLOR_FOLLOWER = '#00FFFF' # Cyan
COLOR_LEADER = '#FF0000' # Red
COLOR_DEAD = '#333333' # Dark Grey
COLOR_GRID = '#003300' # Faint Green
FONT_FAMILY = 'monospace'

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

        if agent_states[aid] == "DEAD":
             agent_states[aid] = "FOLLOWER"

        if RE_LEADER_VICTORY.search(line):
            for i in range(NUM_AGENTS):
                if agent_states[i] == "LEADER":
                    agent_states[i] = "FOLLOWER"
            agent_states[aid] = "LEADER"

def update(frame):
    global file_handle

    # Read new lines
    line = file_handle.readline()
    while line:
        parse_line(line)
        clean_line = line.strip()
        log_lines_buffer.append(clean_line)
        if len(log_lines_buffer) > 25:
            log_lines_buffer.pop(0)
        line = file_handle.readline()

    # Clear and Redraw
    ax_map.clear()
    ax_log.clear()

    # Theme Setup
    ax_map.set_facecolor(COLOR_BG)
    ax_log.set_facecolor(COLOR_BG)
    fig.patch.set_facecolor(COLOR_BG)

    # Status Header
    if system_mode == "DEGRADED":
        status_color = COLOR_TEXT_DEGRADED
        status_text = "STATUS: CRITICAL / MISSION CONTINUITY MODE"
    else:
        status_color = COLOR_TEXT_NORMAL
        status_text = "STATUS: OPERATIONAL / NORMAL"

    ax_map.set_title(f"SWARM COMMAND INTERFACE [v1.0]\n{status_text}",
                     color=status_color, weight='bold', fontfamily=FONT_FAMILY, loc='left')

    # Draw Agents (Radar View)
    radius = 10
    for i in range(NUM_AGENTS):
        angle = 2 * math.pi * i / NUM_AGENTS
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)

        state = agent_states[i]

        if state == "LEADER":
            c = COLOR_LEADER
            m = 'D' # Diamond
            s = 150
            lbl = f"LDR-{i}"
        elif state == "DEAD":
            c = COLOR_DEAD
            m = 'X'
            s = 100
            lbl = f"KIA-{i}"
        else:
            c = COLOR_FOLLOWER
            m = 'o'
            s = 80
            lbl = f"AGT-{i}"

        ax_map.scatter(x, y, c=c, s=s, marker=m, edgecolors='white', linewidth=0.5)
        ax_map.text(x, y+2, lbl, color=c, ha='center', fontsize=8, fontfamily=FONT_FAMILY)

    # Connectivity Lines (Hacker Grid)
    alive_agents = [i for i, s in agent_states.items() if s != "DEAD"]
    for i in range(len(alive_agents)):
        for j in range(i+1, len(alive_agents)):
            a1 = alive_agents[i]
            a2 = alive_agents[j]
            angle1 = 2 * math.pi * a1 / NUM_AGENTS
            angle2 = 2 * math.pi * a2 / NUM_AGENTS
            x1, y1 = radius * math.cos(angle1), radius * math.sin(angle1)
            x2, y2 = radius * math.cos(angle2), radius * math.sin(angle2)
            ax_map.plot([x1, x2], [y1, y2], color=COLOR_GRID, alpha=0.3, linewidth=0.5)

    ax_map.set_xlim(-15, 15)
    ax_map.set_ylim(-15, 15)
    ax_map.axis('off')

    # Log Panel
    ax_log.axis('off')
    log_content = "\n".join(log_lines_buffer)
    ax_log.text(0.02, 0.98, log_content, transform=ax_log.transAxes,
                fontsize=7, color=COLOR_TEXT_NORMAL, fontfamily=FONT_FAMILY,
                verticalalignment='top', wrap=True)

# Setup
fig = plt.figure(figsize=(12, 6))
gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
ax_map = plt.subplot(gs[0])
ax_log = plt.subplot(gs[1])

file_handle = None

def main():
    global file_handle

    print(f"Waiting for {LOG_FILE}...")
    while not os.path.exists(LOG_FILE):
        time.sleep(1)

    file_handle = open(LOG_FILE, 'r')

    ani = animation.FuncAnimation(fig, update, interval=100)
    plt.show()

if __name__ == "__main__":
    main()
