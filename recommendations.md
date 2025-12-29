# Recommendations for Production Hardening

## Priority 1: Critical Fixes
- [x] **Fix Message Parsing Crash**: Completed in Phase 4.
- [ ] **Implement Message Authentication**: Currently messages are unauthenticated. Add HMAC signing to prevent spoofing.

## Priority 2: Performance Optimizations
- [ ] **Binary Serialization**: Switch from JSON to Protobuf/MsgPack for 10x throughput improvement.
- [ ] **Adaptive Throttle**: Adjust 10Hz cycle time dynamically based on CPU load.

## Priority 3: Security Hardening
- [ ] **TLS Encryption**: Encrypt all inter-agent traffic.
- [ ] **Capabilities Verification**: Cryptographically sign capability tokens to prevent agents lying about hardware (S7).

## Priority 4: Monitoring
- [ ] **Prometheus Exporter**: Expose internal agent metrics (cycle time, queue depth) via HTTP.
- [ ] **Centralized Logging**: Ship logs to ELK stack for analysis.
