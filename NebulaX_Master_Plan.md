# PROJECT: NEBULAX FUSION CENTER + ORBITGUARD
**Role:** Senior Cybersecurity Architect & Space Systems Engineer
**Goal:** A "Department-in-a-Box" Cyber-Physical System simulating the defense of terrestrial and orbital assets.

## 1. The Strategic Vision
**"A Mini-Palantir for Space & Cyber."**

We are building a unified **Cyber-Physical Range** that bridges the gap between **USCYBERCOM** and **USSPACECOM**. Unlike standard home labs that focus on one domain, NebulaX demonstrates the **convergence** of orbital mechanics, operational technology (OT), and enterprise security.

It is designed to be a **Flagship Portfolio Artifact** that proves "Hireable Mastery" in:
*   **Space Systems:** SGP4 propagation, Link Budget analysis, and Ground Station operations.
*   **Cyber Warfare:** APT emulation, polymorphic malware, and active defense.
*   **DevSecOps:** Event-driven microservices, "Infrastructure as Code," and secure CI/CD.

## 2. The 5 Strategic Pillars (End State)

### I. The Battlefield (Target Environment)
*   **Concept:** "The Living Network."
*   **End State:** A fully simulated defense contractor ("Astra Dynamics") with a rich digital life.
    *   **`target.identity.manager`:** Simulates thousands of employees generating organic traffic (email, browsing, file access) to create a "noise floor" for the Red Team to hide in.
    *   **`target.internal.infra`:** A simulated Active Directory forest with realistic vulnerabilities (Misconfigured GPOs, Weak ACLs).

### II. Blue Team (Active Defense)
*   **Concept:** "Deception as a Service."
*   **End State:** A sensor grid that moves beyond simple blocking to **Attribution & Intelligence**.
    *   **`blue.honeypot.ssh`:** High-interaction traps that record adversary keystrokes for forensic analysis.
    *   **`blue.sentinel`:** A custom SIEM that correlates network flows with endpoint telemetry to detect "Low and Slow" beacons.

### III. Red Team (Adversary Emulation)
*   **Concept:** "Polymorphic Threat Simulation."
*   **End State:** An attack engine that behaves like a **State Actor (APT)**, not a script kiddie.
    *   **`red.threat.dsl`:** "Attack-as-Code" scenarios defined in YAML.
    *   **`red.apt.emulator`:** Personas that rotate TTPs (Tactics, Techniques, Procedures). If the Blue Team blocks an IP, the Red Team rotates infrastructure (`red.c2.beacon`) and shifts vectors (e.g., SQLi -> Phishing).

### IV. Fusion Layer (The Brain)
*   **Concept:** "Cross-Domain Correlation."
*   **End State:** The "Single Pane of Glass" where physics meets bytes.
    *   **Scenario:** A satellite goes dark (`space.tracker`). The Fusion Center instantly correlates this with a physical breach at the Ground Station (`blue.sentinel`) and a sudden drop in RF signal (`space.rf.receiver`). This is the **Unique Value Proposition** of NebulaX.

### V. OrbitGuard (Space Vertical)
*   **Concept:** "Ethical Grey Research."
*   **End State:** A system that touches the real world.
    *   **`space.tracker`:** Real-time tracking of 20,000+ objects.
    *   **`space.rf.receiver`:** Integration with RTL-SDR hardware to passively capture satellite signals, proving the system connects to physical reality. *Strict adherence to 18 U.S. Code § 1367 (No Interference).*

## 3. Strategic Differentiators (The "X-Factor")

### ⚖️ Law & Policy Integration
**`lex-constellation` (Planned):** A unique module that maps technical events to legal frameworks.
*   *Attack:* "SQL Injection against Satellite C2."
*   *Output:* "Potential violation of CFAA (18 USC 1030) and Outer Space Treaty Article IX."
*   *Why:* Demonstrates readiness for **Space Law** and **GRC** roles.

### 🧠 AI Integration
**`ai.soc` (Planned):** An LLM-based analyst that doesn't just alert, but *explains*.
*   *Input:* Raw JSON logs.
*   *Output:* "Likely Brute Force attempt by APT29 persona. Recommended Action: Isolate Host."
