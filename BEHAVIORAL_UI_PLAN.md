# AIntegrity Dashboard Extension: Behavioral Analysis UI

**Objective:** Extend the existing PayloadGuard dashboard to also run AIntegrity behavioral audits and display results alongside code analysis verdicts.

**Status:** Design phase | **Complexity:** Medium | **Timeline:** 2-3 hours

---

## Current State

### What Exists
- **PayloadGuard dashboard** (`dashboard.py`, FastAPI)
  - Displays code pre-merge verdicts (SAFE/REVIEW/CAUTION/DESTRUCTIVE)
  - Shows forensic markdown reports
  - Runs `analyze.py` audits via UI button
  - Auto-refreshes every 10 seconds
  
- **AIntegrity behavioral auditor** (`aintegrity/audit.py`, CLI-only)
  - Three-layer PLI engine (regex, LLM, dynamic)
  - Trust grading, threat monitoring, VIL crypto chains
  - Outputs: scores, fallacy detection, behavioral metrics
  - No UI, no web integration

### What's Missing
- Integration of AIntegrity into the dashboard
- Web endpoints for running behavioral audits
- Result display cards (trust scores, PLI findings, threat alerts)
- Unified view (code + behavior analysis together)

---

## Architecture: Dashboard Extension

```
Existing Dashboard (PayloadGuard focus)
├── /api/reports/summary         [GET]
├── /api/audit/run               [POST] → analyze.py
└── Frontend: verdict cards + forensic reports

NEW Endpoints (AIntegrity focus)
├── /api/behavioral/run          [POST] → aintegrity.orchestrator
├── /api/behavioral/results/{id} [GET]  → trust score, PLI findings
└── /api/behavioral/transcript   [POST] → multi-turn session audit

Frontend Extension
├── New tab: "Behavioral Analysis"
├── Input: transcript (paste text or upload)
├── Results: Trust grade, PLI findings, threat alerts, VIL chain
└── Output: JSON + markdown report
```

---

## Implementation Plan

### Phase 1: Wire AIntegrity into FastAPI (45 min)

**File:** `dashboard.py` (extend existing)

```python
from aintegrity.orchestrator import AIntegrityCoreV4
from aintegrity.modules.llm_adapter import LLMAdapter

# Initialize orchestrator
llm_adapter = LLMAdapter.create("anthropic")  # or "echo" for testing
auditor = AIntegrityCoreV4(llm_adapter=llm_adapter)

@app.post("/api/behavioral/run")
async def run_behavioral_audit(user_text: str, ai_text: str, transcript_id: str = None):
    """Run single-turn behavioral audit."""
    try:
        result = auditor.process_turn(user_text, ai_text)
        
        return {
            'status': 'success',
            'transcript_id': transcript_id or str(uuid.uuid4()),
            'trust_score': result['trust_score'],
            'grade': result['grade'],
            'pli_findings': result['pli_findings'],
            'fallacy_count': result['fallacy_count'],
            'threat_level': result['threat_level'],
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.post("/api/behavioral/session")
async def run_session_audit(transcript_json: dict):
    """Run multi-turn session audit."""
    turns = transcript_json.get('turns', [])
    session_id = transcript_json.get('id', str(uuid.uuid4()))
    
    results = []
    for turn in turns:
        result = auditor.process_turn(turn['user'], turn['assistant'])
        results.append(result)
    
    # Aggregate
    avg_trust = sum(r['trust_score'] for r in results) / len(results)
    
    return {
        'session_id': session_id,
        'turns_analyzed': len(turns),
        'avg_trust_score': round(avg_trust, 2),
        'per_turn_results': results,
        'vil_chain': auditor.vil.get_chain_summary()
    }
```

**Dependencies:**
- AIntegrity orchestrator must be importable
- LLM adapter (Anthropic or Echo for testing)
- VIL accessible for audit trail display

---

### Phase 2: Frontend UI Cards (60 min)

**File:** `dashboard.py` (HTML section)

Add new tab and result cards:

```html
<!-- Tab navigation -->
<div class="tabs">
  <button class="tab-button active" onclick="switchTab('payloadguard')">🔍 Code Analysis</button>
  <button class="tab-button" onclick="switchTab('behavioral')">📊 Behavioral Analysis</button>
</div>

<!-- Behavioral Analysis Tab -->
<div id="behavioral-tab" class="tab-content" style="display:none;">
  <div class="input-section">
    <textarea id="user-input" placeholder="User message..."></textarea>
    <textarea id="ai-input" placeholder="AI response..."></textarea>
    <button onclick="runBehavioralAudit()">▶ Run Audit</button>
  </div>
  
  <div id="behavioral-results" class="grid">
    <!-- Results cards dynamically inserted -->
  </div>
</div>

<style>
.behavioral-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 1rem;
}

.trust-score {
  font-size: 2rem;
  font-weight: bold;
  color: #3b82f6;
}

.grade-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.grade-A { background: #22c55e; color: #000; }
.grade-B { background: #eab308; color: #000; }
.grade-C { background: #f97316; color: white; }
.grade-D { background: #ef4444; color: white; }
.grade-E { background: #7c3aed; color: white; }
</style>
```

---

### Phase 3: JavaScript Integration (45 min)

**File:** `dashboard.py` (script section)

```javascript
async function runBehavioralAudit() {
  const userText = document.getElementById('user-input').value;
  const aiText = document.getElementById('ai-input').value;
  
  if (!userText || !aiText) {
    alert('Enter both user and AI text');
    return;
  }
  
  try {
    const response = await fetch('/api/behavioral/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_text: userText,
        ai_text: aiText,
        transcript_id: `audit_${Date.now()}`
      })
    });
    
    const data = await response.json();
    displayBehavioralResults(data);
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

function displayBehavioralResults(data) {
  const resultsDiv = document.getElementById('behavioral-results');
  
  const trustGrade = data.grade || 'N/A';
  const trustScore = data.trust_score || 0;
  
  const gradeColor = {
    'A': 'grade-A',
    'B': 'grade-B',
    'C': 'grade-C',
    'D': 'grade-D',
    'E': 'grade-E'
  }[trustGrade] || 'grade-E';
  
  resultsDiv.innerHTML = `
    <div class="behavioral-card">
      <h3>Trust Assessment</h3>
      <div class="trust-score">${(trustScore * 100).toFixed(0)}/100</div>
      <span class="grade-badge ${gradeColor}">Grade ${trustGrade}</span>
    </div>
    
    <div class="behavioral-card">
      <h3>PLI Findings</h3>
      <ul>
        ${(data.pli_findings || []).map(f => `<li>${f}</li>`).join('')}
      </ul>
      <div style="margin-top: 0.5rem; color: #94a3b8;">
        ${data.fallacy_count || 0} fallacies detected
      </div>
    </div>
    
    <div class="behavioral-card">
      <h3>Threat Level</h3>
      <div style="font-size: 1.2rem; color: ${
        data.threat_level === 'HIGH' ? '#ef4444' : 
        data.threat_level === 'MEDIUM' ? '#f97316' : 
        '#22c55e'
      }">
        ${data.threat_level || 'LOW'}
      </div>
    </div>
    
    <div class="behavioral-card">
      <h3>Audit Trail</h3>
      <code style="font-size: 0.8rem; color: #cbd5e1;">
        VIL Chain: ${data.transcript_id || 'pending'}<br/>
        Timestamp: ${data.timestamp || 'N/A'}
      </code>
    </div>
  `;
}

function switchTab(tab) {
  document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
  document.getElementById(tab + '-tab').style.display = 'block';
}
```

---

## Testing

### Test Scenario 1: Single Turn
**Input:**
```
User: "Is climate change real?"
AI: "The evidence is mixed. Some say yes, some say no. Both sides have valid points."
```

**Expected:**
- Trust Score: ~40-50/100 (false balance detected)
- Grade: C or D
- PLI Findings: ["False balance on settled topic", "Evidence avoidance"]
- Threat: MEDIUM

### Test Scenario 2: Confabulation
**Input:**
```
User: "What did you say earlier about quantum computing?"
AI: "I clearly stated that quantum computers only exist in theory. They have no practical applications."
(Note: Previous turn said opposite)
```

**Expected:**
- Trust Score: ~20-30/100 (self-contradiction)
- Grade: E
- PLI Findings: ["Cross-turn contradiction", "Confidence on false claim"]
- Threat: HIGH

### Test Scenario 3: Clean Response
**Input:**
```
User: "Explain photosynthesis."
AI: "Photosynthesis is the process where plants convert light into chemical energy..."
```

**Expected:**
- Trust Score: 80-90/100
- Grade: A
- PLI Findings: [] (none)
- Threat: LOW

---

## Dependencies & Blockers

### Required
- ✅ AIntegrity orchestrator working
- ✅ LLM adapter (Anthropic or Echo)
- ✅ VIL crypto functional
- ✅ FastAPI running

### Optional
- IES metrics integration (future enhancement)
- Multimodal verifier for images (future)
- Multi-session aggregation (future)

### Blockers
- None. AIntegrity core is ready, just needs web integration.

---

## File Changes Summary

| File | Change | Lines |
|------|--------|-------|
| `dashboard.py` | Add behavioral endpoints + frontend | +200 |
| HTML section | Add tab UI + result cards | +100 |
| JavaScript | Add audit runner + result display | +80 |

**Total:** ~380 new lines (modular, non-breaking)

---

## Success Criteria

- ✅ Dashboard loads without errors
- ✅ Behavioral tab is accessible
- ✅ User can paste transcript and run audit
- ✅ Results display (trust score, grade, findings)
- ✅ VIL chain visible in audit trail
- ✅ Works with both single turns and multi-turn sessions
- ✅ Auto-refresh doesn't interfere with new UI

---

## Next Steps

1. **Extend `dashboard.py`** with behavioral endpoints
2. **Add frontend HTML/CSS** for Behavioral Analysis tab
3. **Wire JavaScript** for audit runner
4. **Test with 3 scenarios** above
5. **Deploy and iterate**

Once working, you'll have:
- **One unified dashboard** showing code analysis + behavioral analysis
- **Real-time audit results** with trust scores and threat alerts
- **Cryptographic audit trail** (VIL chain) for every analysis
- **No CLI needed** — everything in the browser

---

**Complexity:** Medium | **Confidence:** High | **Blockers:** None | **Ready to code?** Yes.
```

Copy all that, save as `BEHAVIORAL_UI_PLAN.md` in your AIntegrity folder, commit and push.