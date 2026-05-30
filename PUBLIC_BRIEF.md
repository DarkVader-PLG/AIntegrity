# AIntegrity — Public Brief

Behavioural auditing framework for AI systems. Detects logical inconsistency, evasion, hallucination, and epistemic drift in LLM outputs through automated multi-layer analysis with a cryptographically verifiable audit trail.

**Author:** Steven Dark | Independent AI Safety Researcher | Aberdeen, Scotland

---

## Problem — Epistemic Decay in AI Systems

Large language models contradict themselves across conversation turns, evade direct questioning through deflection and hedging, and drift semantically over extended interactions. Current evaluation methods (benchmarks, RLHF, constitutional AI) measure alignment at training time but provide no mechanism for detecting when a deployed system's epistemic integrity degrades during use.

The consequences are not theoretical. An LLM that claims capability in turn 3 and denies it in turn 7 is not just inconsistent — it is unauditable. Any system built on top of such a model inherits its epistemic failures silently.

**Central thesis:** *Alignment presupposes epistemology. A perfectly aligned system operating on corrupted context will faithfully pursue a corrupted goal.*

AIntegrity provides the instrumentation to detect when that corruption occurs.

---

## Approach — Persistent Logical Interrogation (PLI)

A three-layer pipeline that detects logical failures in AI responses through escalating analysis.

### Layer 1 — Regex (Fast, Zero-Cost)

Pattern matching for known failure signatures:

| Detector | What It Catches |
|---|---|
| Cross-turn contradiction | AI claims capability in turn N, denies it in turn N+M |
| Evasion | Refusal patterns, topic changes, capability denial |
| Hedging | Commitment avoidance — "perhaps", "it could be argued" |
| Circular reasoning | Self-referential justification loops |
| Meta-apology loops | Repeated "I apologize for the confusion" with escalating severity |
| False authority | Unsourced "studies show", "experts agree" |
| Deflection | Topic redirection to avoid direct answers |
| Self-contradiction | Contradictory claims within a single response |

### Layer 2 — LLM Dual-Pass (Semantic)

Two independent LLM interrogations of each AI response:

- **OBSERVE pass:** Structured analysis for factual errors, logical fallacies, unsupported claims, semantic coherence.
- **VERIFY pass:** Adversarial re-examination challenging every claim from the OBSERVE pass.
- **Variance tracking:** Score difference between passes is itself a signal — high variance indicates borderline findings.

### Layer 3 — Dynamic Prompting

L1 findings steer L2 interrogation. Surface-level pattern detection guides deep semantic analysis through an adaptive feedback loop — hedging detection triggers commitment evasion focus, circular reasoning triggers adversarial interrogation mode.

### PLI 5-State Interrogation Cycle

The methodology operates as a formal state machine:

| State | Function |
|---|---|
| **CONFRONT** | Present the AI with evidence of inconsistency |
| **DETECT** | Identify the specific failure mode from 9 categories |
| **COUNTER** | Apply targeted counter-interrogation |
| **ESCALATE** | Increase adversarial pressure if evasion persists |
| **FORCE** | Demand explicit resolution — no hedging permitted |

Nine categorised failure modes provide structured classification of every detected integrity violation.

---

## Components

### Trust Grading Engine

Weighted multi-dimensional trust score with temporal decay:

| Component | Weight |
|---|---|
| Logical consistency | 0.25 |
| Factual accuracy | 0.20 |
| Visual consistency | 0.15 |
| Behavioral stability | 0.20 |
| Adversarial resistance | 0.20 |

Trust decays over time using a logistic function. Negative events (contradictions, confirmed deception) apply immediate penalties and accelerate future decay. Grades: **A** (80+) through **E** (<20).

### Adversarial Threat Monitor

Real-time detection of prompt injection and model evasion: 11 compiled regex patterns for injection, 6 for evasion, Population Stability Index (PSI) for response distribution drift, vocabulary overlap tracking.

### Verifiable Interaction Ledger (VIL)

Every event — user input, model output, analysis finding, trust score — is recorded with:

- **SHA-256 hash chain** — each event's hash includes the previous event's hash, creating a tamper-evident sequence.
- **Ed25519 digital signatures** — each event is signed with a session-specific key pair.
- **Merkle tree anchoring** — session sealing produces a Merkle root over all event hashes.

Chain integrity is independently verifiable at any time.

### Multimodal Verifier (Optional)

CLIP-based image-text consistency scoring and perceptual hashing for media integrity assessment.

---

## Research Context

Two papers formalise the theoretical foundations:

- **Dark, S. (2026).** *Epistemic Decay in Agentic AI Systems.* Formalises the systematic degradation of epistemic agency through AI interaction — the phenomenon AIntegrity is built to detect.

- **Dark, S. (2026c).** *Persistent Logical Interrogation: A Formal Methodology for Behavioural Consistency Auditing in Large Language Models.* Specifies the PLI methodology as a five-state interrogation cycle with nine categorised failure modes.

---

## Verification

- **217 tests** covering all modules (PLI engine, trust grading, threat monitoring, VIL integrity, LLM adapter, orchestrator).
- **Deterministic `EchoBackend`** for LLM-dependent tests — full test suite runs with zero API cost and deterministic results.
- **No mandatory external dependencies** for core functionality (L1 regex + VIL hash chain).

---

## Classification

This brief contains **Tier 1 (Fully Public)** content only. See [`DISCLOSURE_STRATEGY.md`](https://github.com/PayloadGuard-PLG/payload-consequence-analyser/blob/main/DISCLOSURE_STRATEGY.md) in the PayloadGuard repository for the full classification framework.

---

*Built solo, from a phone, using AI-directed development. Three months. No team, no IDE, no desktop.*
