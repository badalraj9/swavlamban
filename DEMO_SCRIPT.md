# Swavlamban 2025 - Challenge 1 Demo Script

**Total Duration**: 5:00 minutes

---

### 0:00 - 0:30: Problem & Constraints
**(Visual: Diagram of distributed swarm nodes with lossy radio links)**

**Narrator**: "Welcome to the Swavlamban 2025 submission for Challenge 1. We address the problem of distributed swarm coordination under severe network constraints. Our system operates without a central server, utilizing a 64kbps lossy radio link, and maintains a strictly real-time 10Hz update loop. The solution prioritizes simplicity and robustness, avoiding heavy cryptographic overhead to ensure maximum reliability on embedded hardware."

### 0:30 - 1:30: Scenario S6 - Leader Failure & Re-election
**(Visual: Terminal showing Agent 9 (Leader) being killed. Logs show Agent 8 taking over)**

**Narrator**: "Here we demonstrate the system's resilience to leader failure. We simulate a catastrophic failure of the current leader, Agent 9. Watch as the system detects the silence within 2 seconds. The Bully Algorithm immediately triggers a new election. Agent 8 promotes itself, broadcasts a Coordinator claim, and the swarm converges on the new leader in under 4 seconds—well within the 10-second requirement. Note the seamless transition; the swarm state remains consistent."

### 1:30 - 2:30: Scenario S7 - Capability-Aware Task Allocation
**(Visual: Map or Log view showing tasks with 'heavy_lift' requirement appearing)**

**Narrator**: "Next, we showcase the Consensus-Based Auction Algorithm (CBAA) handling complex task allocation. We inject 100 tasks, some requiring specific capabilities like 'heavy_lift'. You can see agents filtering tasks they cannot perform. The auction converges rapidly, resolving conflicts using the Max-Consensus rule. In this run, 99 out of 100 tasks are assigned and stable within 30 seconds, satisfying the 95% stability gate."

### 2:30 - 3:20: Adversarial Testing - Security in Action
**(Visual: Highlight log scrolling with 'SECURITY: UUID mismatch' warnings)**

**Narrator**: "Our development process included a rigorous 'Hell-Test' phase. Here, a malicious agent attempts to spoof the leader by broadcasting fake Coordinator messages. Observe the logs: 'SECURITY: UUID mismatch - message ignored'. Our hardening strategy—binding Identity to a random Boot UUID and Monotonic Term—allows honest agents to instantly detect and discard these spoofed commands. The attack is neutralized without disrupting the swarm's operation."

### 3:20 - 4:20: Network Chaos & Resilience
**(Visual: Packet loss graph or logs showing dropped packets but continued operation)**

**Narrator**: "We push the system further by injecting 50% packet loss. Despite half the messages failing to arrive, the robust state machine holds together. The leadership remains stable, and tasks continue to be processed. This resilience is key for real-world deployment where radio conditions are unpredictable."

### 4:20 - 5:00: Conclusion
**(Visual: Summary slide with 'PASSED - PRODUCTION READY')**

**Narrator**: "In conclusion, this submission demonstrates a Production-Ready distributed system. We have met all performance gates: Leader Election under 10s, Stability over 95%, and Real-Time performance at 10Hz. By focusing on minimal, effective hardening, we deliver a secure and robust solution ready for the challenges of Swavlamban. Thank you."

---
