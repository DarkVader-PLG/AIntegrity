# AIntegrity — Public Brief

**Behavioral auditing framework for AI systems.**

---

## Problem

AI systems produce outputs that are logically inconsistent, evasive, or epistemically corrupted — and do so in ways that are difficult for humans to detect in real time. Current evaluation methods rely on benchmarks (static) or human review (unscalable). There is no production-grade framework for continuous, automated behavioral auditing with cryptographic proof of findings.

AIntegrity answers: **is this AI system saying things that are logically consistent, factually grounded, and free from evasion?**

---

## Central Thesis

> Alignment presupposes epistemology. A perfectly aligned system operating on corrupted context will faithfully pursue a corrupted goal. AIntegrity provides the instrumentation to detect when that corruption occurs.

This framework implements the detection layer for Epistemic Decay — the systematic degradation of epistemic agency through AI interaction.

---

## Architecture

```
                      ┌──────────────────────┐
                      │     Orchestrator      │
                      │   AIntegrityCoreV4    │
                      └──────────┬───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   PLI Engine     │   │  Trust Grading   │   │ Threat Monitor  │
│  (Three-Layer)   │   │    Engine v4     │   │  (Adversarial)  │
└────────┬────────┘   └─────────────────┘   └─────────────────┘
         │
┌────────┼────────┐
│        │        │
▼        ▼        ▼
L1      L2      L3
Regex   LLM    Dynamic
        Dual   Prompting
        Pass
         │
         ▼
┌─────────────────┐       ┌─────────────────┐
│   LLM Adapter    │       │    Multimodal    │
│ OpenAI/Anthropic │       │    Verifier      │
└─────────────────┘       │  (CLIP / phash)  │
                           └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│    Verifiable Interaction Ledger (VIL)   │
│  SHA-256 hash chain + Merkle tree + sigs │
└─────────────────────────────────────────┘
```

---

## PLI — Persistent Logical Interrogation

A five-state interrogation cycle for behavioral consistency auditing:

**CONFRONT → DETECT → COUNTER → ESCALATE → FORCE**

The PLI engine operates across three detection layers:

| Layer | Method | Cost | What it catches |
|-------|--------|------|-----------------|
| L1 | Compiled regex patterns | Zero | Cross-turn contradictions, evasion, hedging, circular reasoning, false authority |
| L2 | LLM dual-pass (OBSERVE + VERIFY) | API call | Factual errors, logical fallacies, unsupported claims, semantic coherence |
| L3 | Dynamic prompting | Adaptive | L1 findings steer L2 focus — hedging triggers commitment interrogation, circular reasoning triggers adversarial mode |

Nine categorised failure modes. Variance between L2 passes is itself a signal — high variance indicates uncertain findings.

---

## Trust Grading Engine

Weighted multi-dimensional trust score with temporal decay:

| Component | Weight | Source |
|-----------|--------|--------|
| Logical consistency | 0.25 | PLI Engine |
| Factual accuracy | 0.20 | Citation verification |
| Visual consistency | 0.15 | CLIP image-text matching |
| Behavioral stability | 0.20 | Session drift detection |
| Adversarial resistance | 0.20 | Threat monitor |

Trust decays over time via logistic function. Negative events apply immediate penalties and increase future decay rate.

Grades: **A** (80+) · **B** (60+) · **C** (40+) · **D** (20+) · **E** (<20)

---

## Verifiable Interaction Ledger (VIL)

Every event — user input, model output, analysis finding, trust score — is recorded with:

- **SHA-256 hash chain:** Each event includes the previous event's hash (tamper-evident)
- **Ed25519 digital signatures:** Session-specific key pair signs each event
- **Merkle tree anchoring:** Session sealing produces a Merkle root over all event hashes
- **Timestamp authority:** RFC 3161 TSA integration
- **Chain integrity verification:** `verify_chain_integrity()` detects any tampering at any point

---

## Adversarial Threat Monitor

Real-time detection of prompt injection and model evasion:

- 11 compiled regex patterns for injection detection
- 6 patterns for evasion and capability denial
- Population Stability Index (PSI) for response distribution drift
- Vocabulary drift tracking against session baselines
- Threat levels: 0.9 (injection) → 0.6 (drift) → 0.5 (evasion) → 0.3 (moderate drift)

---

## Behavioral Metrics

- **CFR (Confabulation Rate):** Fallacies detected / total turns
- **RR (Refusal Rate):** Evasions detected / total turns
- **AD (Admission Detection):** Self-admitted errors / total turns

---

## Technology Stack

- **Core:** Python, FastAPI, GitPython
- **Analysis:** Z3-Solver, Abstract Syntax Trees, spaCy
- **LLM integration:** Anthropic API, OpenAI API (provider-agnostic adapter)
- **Cryptography:** Ed25519 (signatures), SHA-256 (hash chain), Merkle trees
- **Multimodal:** CLIP (image-text consistency), pHash (media integrity)
- **Persistence:** PostgreSQL

---

## Development Context

- **Timeline:** 3 months (March–May 2026)
- **Developer:** Solo — Steven Dark (Aberdeen, Scotland)
- **Method:** AI-directed development. Human designs and architects; AI implements under direction.
- **Research basis:** "Epistemic Decay in Agentic AI Systems" (Dark, 2026), "Persistent Logical Interrogation" (Dark, 2026c)

---

## What This Demonstrates

1. **AI safety engineering** — production-grade behavioral auditing beyond benchmarks
2. **Cryptographic systems design** — tamper-evident audit trail with multiple verification layers
3. **Adversarial analysis** — systematic detection of injection, evasion, and drift
4. **Research translation** — formal methodology (PLI) implemented as working software
5. **LLM integration architecture** — provider-agnostic dual-pass analysis with variance tracking

---

## Contact

For research collaboration, private demonstration, or employment enquiries: see the [portfolio page](https://payloadguard-plg.github.io/payload-consequence-analyser/) or contact Steven Dark directly via [GitHub](https://github.com/DarkVader-PLG).
