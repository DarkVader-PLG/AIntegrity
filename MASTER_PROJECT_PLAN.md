```
# AIntegrity: Master Project Plan

**Status:** Active Development | **Last Updated:** April 20, 2026 | **Author:** Steven Dark

---

## I. PROJECT VISION (24-Module Architecture)

**Ultimate Goal:** Cryptographically-auditable behavioral analysis system for AI systems that detects integrity failures, proves them cryptographically, and gates dangerous changes before they're deployed.

**Core Principle:** *Alignment presupposes epistemology. A perfectly aligned system operating on corrupted context will faithfully pursue a corrupted goal.*

**The 24-Module Vision** (consolidated from 1,500+ files, 271 Gemini architecture discussions):
- Full architectural designs exist in `/docs/` PDFs
- Development documents + research + code specs in those files
- Current session focuses on: **PayloadGuard (code pre-merge gate) + behavioral risk detection + dashboard**
- Next phases: Integrate IES, wire Sentinel Enforcement Core, connect remaining 20 modules

---

## II. CURRENT STATE (April 20, 2026)

### What's Built & Working

**PayloadGuard** (5-Layer Pre-Merge Analysis)
- L1: Surface scan (intent extraction, red flag detection)
- L2: Deep forensic analysis (file/line counts, temporal analysis)
- L3: Consequence assessment (severity scoring)
- L4: Structural drift detection (Python AST analysis)
- L4.5: [READY TO IMPLEMENT] Behavioral risk detection (critical file protection)
- L5: Observations (presentation/payload mismatch detection)
- **Output:** SAFE/REVIEW/CAUTION/DESTRUCTIVE verdicts + forensic markdown reports
- **Status:** ✅ Working, tested against 6 scenarios

**Dashboard** (Web UI for Reports)
- View PayloadGuard verdicts + forensic reports
- View drift scores + trends
- View IES reports
- Run audits via UI (no CLI needed)
- Auto-refresh every 10 seconds
- **Status:** ✅ Ready to use (http://localhost:8765)

**Forensic Report Generator**
- 6-section markdown narrative
- JSON + markdown output modes
- Layer 5 observations (narrative interpretation)
- **Status:** ✅ Working

### What's Ready to Code (Layer 4.5)

**Behavioral Risk Detector**
- Protects critical files: `vil.py`, `pli_analyzer.py`, `orchestrator.py`, `threat_monitor.py`
- Escalates to DESTRUCTIVE if behavior-critical files modified with high structural drift
- Configuration-driven (YAML)
- **Code structure:** Ready in IMPLEMENTATION_PLAN.md (Phase 2)
- **Timeline:** 60-90 min coding + 60-120 min iteration
- **Status:** 🔄 Code ready, awaiting integration

### What's Mapped But Not Integrated

**IES Metrics Framework** (7 metrics, 11 failure tags)
- FBS2: False balance detection
- EUS: Evidence use scoring
- TCC: Tier-calibrated confidence
- NAI: Narrative amplification
- ABC: Attribution boundaries
- CS: Consistency
- SCS: Stance consistency
- **Mapped to:** Code behavioral concepts (false balance in code logic, evasion in error handling, etc.)
- **Status:** 🔄 Conceptually mapped, integration strategy designed, not yet wired

**Drift Detector** (Conversation Continuity)
- Measures deviation from reference
- Flagging thresholds (0.40 aligned, 0.60 flagged)
- **Mapped to:** Architectural drift patterns
- **Status:** 🔄 Conceptually mapped, not yet integrated

---

## III. INTEGRATION ARCHITECTURE

### What Connects to What

```

PayloadGuard (L1-L5)
├── Feeds to: Behavioral Risk Detector (L4.5)
│   └── Uses: behavioral_critical_files.yaml config
│
├── Feeds to: Forensic Report Generator
│   └── Output: Markdown + JSON
│
└── Feeds to: Dashboard
    └── Displays: Verdicts + reports
    
    IES Metrics (Separate System)
    ├── Measures: Behavioral problems in transcripts
    ├── Bridges to: PayloadGuard via critical-file mapping
    │   └── Concept: If these files change → behavioral problems possible
    └── Not integrated: Full metric computation not needed for code analysis
    
    Drift Detector (Separate System)
    ├── Measures: Conversation continuity
    ├── Bridges to: PayloadGuard via pattern mapping
    │   └── Concept: Architectural drift ≠ conversation drift
    └── Not integrated: Concept borrowed, not system imported
    
    Sentinel Enforcement Core (To Be Wired)
    ├── Purpose: Cryptographic proof chains
    ├── Integrates with: VIL (Verifiable Interaction Ledger)
    ├── Feeds to: PayloadGuard verdicts
    └── Produces: Tamper-proof audit trail
    
    ```
    
    ### Key Decision: NO FORCE-FIT INTEGRATION
    
    **What makes sense:**
    - PayloadGuard + Behavioral Risk Detector ✅ (same domain: code)
    - IES concepts → critical-file mapping ✅ (behavioral awareness for code)
    - Drift concepts → architectural patterns ✅ (borrowed, not imported)
    
    **What doesn't:**
    - Running IES on code directly ❌ (IES expects transcripts)
    - Applying drift detector to diffs ❌ (conversation metric ≠ code metric)
    - Forcing all three into one system ❌ (different domains, different logic)
    
    ---
    
    ## IV. IMMEDIATE NEXT STEPS (This Week)
    
    ### Phase 1: Consolidate Locally (Your PC)
    1. Pull entire AIntegrity repo
    2. Transfer 1,500+ files from your backups
    3. Organize: architecture docs, Gemini conversations (271), screenshots, videos, code
    4. Goal: Single source of truth on your PC
    
    ### Phase 2: Review Full Architecture (With Claude on Your PC)
    1. Open PDFs from `/docs/`
    2. Review module specs from development documents
    3. Map all 24 modules and their dependencies
    4. Identify which 5-10 modules are most critical to implement next
    5. Understand Sentinel Enforcement Core role in the system
    
    ### Phase 3: Implement Layer 4.5 (60-90 min)
    Follow IMPLEMENTATION_PLAN.md:
    1. Create `behavioral_risk_detector.py`
    2. Add `behavioral_critical_files.yaml`
    3. Integrate into `analyze.py` (Layer 4.5)
    4. Test against scenarios C, D, E
    5. Calibrate thresholds
    
    ### Phase 4: Test & Iterate (60-120 min)
    1. Run all 6 scenarios
    2. Validate verdicts
    3. Adjust thresholds for your codebase patterns
    4. Test edge cases
    5. Commit and document
    
    ### Phase 5: Extend to Next Module
    Once Layer 4.5 is working, pick the next critical module from the 24-module list and repeat.
    
    ---
    
    ## V. TECHNICAL DETAILS
    
    ### PayloadGuard Verdicts
    
    | Verdict | Meaning | Action |
    |---------|---------|--------|
    | **SAFE** | No red flags, code changes look clean | Merge allowed |
    | **REVIEW** | Some concerns, needs human inspection | Manual review required |
    | **CAUTION** | Significant changes, high risk | Block until reviewed |
    | **DESTRUCTIVE** | Deletes core files or behavior-critical logic | Block, escalate to security team |
    
    ### Layer 4.5 Thresholds (Calibrated Guesses)
    
    | File | Tier | Drift Threshold | Trigger |
    |------|------|-----------------|---------|
    | `vil.py` | TIER_1 | 1.0 | Deletion or high drift → DESTRUCTIVE |
    | `pli_analyzer.py` | TIER_1 | 1.5 | High drift → DESTRUCTIVE |
    | `threat_monitor.py` | TIER_1 | 1.5 | High drift → DESTRUCTIVE |
    | `orchestrator.py` | TIER_1 | 2.0 | Deletion → DESTRUCTIVE |
    
    *Note: These thresholds will be adjusted after testing against real codebase patterns.*
    
    ### File Organization
    
    ```
    
    ~/AIntegrity/
    ├── Core System
    │   ├── analyze.py                    # PayloadGuard (L1-L5)
    │   ├── behavioral_risk_detector.py   # L4.5 [TO CODE]
    │   └── dashboard.py                  # Web UI
    │
    ├── Configuration
    │   ├── behavioral_critical_files.yaml # L4.5 config
    │   └── INTEGRATION_MAP.md            # Tier definitions
    │
    ├── Documentation
    │   ├── MASTER_PROJECT_PLAN.md        # This file (master reference)
    │   ├── HANDOVER.md                   # Session handover
    │   ├── PAYLOADGUARD_SYSTEM_WHITEPAPER.md # Full system docs
    │   ├── IES_DRIFT_PAYLOADGUARD_ANALYSIS.md # Integration strategy
    │   ├── IMPLEMENTATION_PLAN.md        # Step-by-step coding
    │   └── DASHBOARD_QUICKSTART.md       # UI guide
    │
    ├── Testing
    │   ├── payloadguard_test_suite.py    # Test scenarios
    │   └── tests/                        # Unit tests (217 passing)
    │
    └── Original Core System (Not Active)
        ├── aintegrity/
            ├── Epistemic_Decay_v2.pdf
                └── [Legacy modules]
                
                ```
                
                ---
                
                ## VI. DEPENDENCIES & BLOCKERS
                
                ### No Current Blockers
                - ✅ Code works
                - ✅ Tests pass
                - ✅ Architecture clear
                - ✅ Integration plan defined
                
                ### Dependencies for Next Phase
                1. **Review 24-module architecture** (on your PC) → understand Sentinel Enforcement Core role
                2. **Decide module priority** → which 5 modules after Layer 4.5?
                3. **Understand crypto integration** → how VIL chains connect to Sentinel
                
                ---
                
                ## VII. CREDIT OPTIMIZATION STRATEGY
                
                **You're on Haiku now (cheap, structural).** Smart.
                
                When consolidating 1,500 files on your PC:
                1. **Convert to markdown/text** (not PDFs or images)
                2. **Paste excerpts, not full files** (5-10 relevant sections per session)
                3. **Reference locally** (don't re-upload same docs)
                4. **Switch to Sonnet/Opus only when logic-heavy** (Layer 4.5 integration, module design)
                
                **Expected credit savings:** 70-80% vs. uploading everything every session.
                
                ---
                
                ## VIII. WORKING LOCALLY WITH CLAUDE
                
                **Optimal setup on your PC:**
                
                ```
                
                Terminal 1: python dashboard.py (leave running)
                Terminal 2: Your IDE (code changes)
                Terminal 3: git (commits)
                Browser: http://localhost:8765 (auto-refreshing reports)
                Chat: Claude (guidance + debugging)
                ```
                
                **Workflow:**
                1. Make code change in IDE
                2. Run audit via dashboard (no CLI)
                3. See results immediately
                4. Ask Claude questions based on results
                5. Iterate until tests pass
                6. Commit
                
                **No context switching.** Everything on one screen.
                
                ---
                
                ## IX. SUCCESS CRITERIA
                
                ### Layer 4.5 Complete When:
                - ✅ `behavioral_risk_detector.py` implemented
                - ✅ `behavioral_critical_files.yaml` configured
                - ✅ All 6 test scenarios pass
                - ✅ Thresholds calibrated to your codebase
                - ✅ Edge cases handled
                - ✅ Documented in code + HANDOVER.md
                
                ### Full System Ready When:
                - ✅ PayloadGuard + behavioral detection integrated
                - ✅ Dashboard showing all report types
                - ✅ IES framework integrated (metrics feeding into analysis)
                - ✅ Sentinel Enforcement Core wired in (crypto proof chains)
                - ✅ 5-10 critical modules from 24-module vision implemented
                - ✅ Consolidated architecture document (all 24 modules mapped)
                
                ---
                
                ## X. KEY PRINCIPLES
                
                1. **Test first, optimize second** — Get it working, then make it elegant
                2. **Document decisions** — Why this threshold? Why this integration point? Write it down.
                3. **Iterate with real patterns** — Thresholds from generic test repos don't work. Use your actual code.
                4. **No force-fit integration** — If two systems don't naturally connect, they shouldn't.
                5. **Evidence over assumptions** — Screenshots, videos, test results. Not hunches.
                
                ---
                
                ## XI. RESOURCES
                
                ### Documentation (Read in This Order)
                1. **This file** — Master overview (you're here)
                2. **HANDOVER.md** — Detailed session status
                3. **PAYLOADGUARD_SYSTEM_WHITEPAPER.md** — Full system docs
                4. **IMPLEMENTATION_PLAN.md** — Next phase coding (6 steps)
                5. **IES_DRIFT_PAYLOADGUARD_ANALYSIS.md** — Integration strategy
                6. **DASHBOARD_QUICKSTART.md** — How to use UI
                
                ### On Your PC (Consolidate These)
                - 1,500+ development files
                - 271 Gemini conversations (architecture discussion)
                - /docs/ PDFs (full 24-module specs)
                - Screenshots + videos (real-time failures and successes)
                - All code (current repo + any legacy modules)
                
                ### When Starting New Claude Session
                - Paste link to this file
                - Reference sections by number
                - Paste relevant code excerpts (not full files)
                - Share screenshot of dashboard results (for context)
                
                ---
                
                ## XII. NEXT CLAUDE SESSION CHECKLIST
                
                When you start a new session on your PC:
                
                - [ ] Read this MASTER_PROJECT_PLAN.md (sections I-IV)
                - [ ] Read IMPLEMENTATION_PLAN.md (Phase 2-4)
                - [ ] Review current `analyze.py` (understand L1-L5)
                - [ ] Check test scenarios in `payloadguard_test_suite.py`
                - [ ] Ask: "What's blocking Layer 4.5 implementation?"
                - [ ] Code, test, iterate
                - [ ] Update HANDOVER.md before committing
                
                ---
                
                ## XIII. FINAL NOTES
                
                **This is not the final system.** This is the checkpoint where:
                - PayloadGuard works
                - Behavioral risk detection is ready to code
                - Dashboard eliminates friction
                - Integration strategy is clear
                - 24-module vision is documented
                
                **What you're actually building:**
                A pre-merge gate that doesn't just detect destructive changes—it understands *behavioral* implications of those changes. It proves them cryptographically. It gates them before deployment.
                
                That's not just a tool. That's a supply chain security layer.
                
                **One step at a time.**
                
                ---
                
                **Created:** April 20, 2026  
                **Author:** Steven Dark (@DarkVader)  
                **Status:** Ready for Layer 4.5 implementation  
                **Next Session:** Consolidate locally, review architecture, code L4.5
```
