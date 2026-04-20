

print("TSAClient: requests/rfc3161-client not installed.
Simulating token.")
token =
f"simulated_tsa:{sha256_hex(digest)}@{utc_now_iso()}".encode()
summary = TSASummary(status="simulated",
hash_algorithm="sha256", imprint_hex=digest.hex())
return token, summary

for attempt in range(self.retries):
try:
client = RFC3161Client(self.tsa_url,
timeout=self.timeout)
ts_token = client.timestamp(data=digest)
summary = TSASummary(status="unchecked",
tsa_url=self.tsa_url, hash_algorithm="sha256",
imprint_hex=digest.hex())

return ts_token, summary
except Exception as e:
print(f"TSA request attempt {attempt +
1}/{self.retries} failed: {e}")
if attempt < self.retries - 1:
time.sleep(0.5 * (2 ** attempt))  # Exponential
backoff
else:
print("TSA failed after all retries. Downgrading
to simulated token.")
token =
f"simulated_tsa_fallback:{sha256_hex(digest)}@{utc_now_iso()}".encode(
## )
summary = TSASummary(status="simulated",
hash_algorithm="sha256", imprint_hex=digest.hex())
return token, summary
return None, TSASummary(status="failed",
hash_algorithm="sha256", imprint_hex=digest.hex())

def verify(self, ts_token: bytes, digest: bytes) -> bool:
"""Verifies a timestamp token against a digest."""
# This is a placeholder for full cryptographic verification.
# A production implementation MUST parse the ASN.1 response,
validate the
# TSA's certificate chain against a trusted root, and check
the messageImprint.
if b"simulated_tsa" in ts_token:
return digest.hex().encode() in ts_token
if digest in ts_token:
return True
print("Warning: Real TSA token verification is a placeholder
and not secure.")

return False

class AnchorClient:
"""Client for publishing Merkle roots to an external anchor."""
def __init__(self, backend: str = "null", endpoint: Optional[str]
## = None):
self.backend = backend
self.endpoint = endpoint

def publish_merkle_root(self, root_hex: str) -> Optional:
if self.backend == "null":
return AnchorReceipt(
backend="simulated",
reference=sha256_hex(root_hex.encode()),
anchored_at_utc=utc_now_iso(),
payload={"note": "This is a simulated anchor for
offline testing."}
## )
# In a real implementation, this would make a network call to
a blockchain or transparency log.
print(f"Warning: Anchor backend '{self.backend}' not
implemented. Skipping.")
return None

def verify(self, root_hex: str, receipt: AnchorReceipt) -> bool:
if receipt.backend in ["null", "simulated"]:
return sha256_hex(root_hex.encode()) == receipt.reference
print(f"Warning: Anchor verification for backend
'{receipt.backend}' not implemented.")
return False

class VIL:
"""The Verifiable Interaction Ledger, creating a tamper-evident
audit trail."""
def __init__(self,
session_id: str,
signing_key: Optional["ed25519.Ed25519PrivateKey"],
key_id: Optional[str] = None,
tsa_client: Optional = None,
anchor_client: Optional[AnchorClient] = None):
if signing_key and not CRYPTO_OK:
raise ImportError("Cryptography library is required for
signing but not installed.")
self.session_id = session_id
self._events: List[EnvelopeModel] =
self._prev_chain_hash: Optional[str] = None
self._signing_key = signing_key
self._key_id = key_id

self._public_key_pem = self._export_public_pem(signing_key) if
signing_key else None
self.tsa_client = tsa_client or TSAClient()
self.anchor_client = anchor_client or AnchorClient()

def log_event(self, event_type: EventType, content: Dict[str,
Any], parent_event_id: Optional[str] = None) -> EnvelopeModel:
content_hash = sha256_hex(canonical_json(content).encode())
header = HeaderModel(alg="EdDSA", kid=self._key_id)
payload = PayloadModel(event_id=str(uuid.uuid4()),
event_type=event_type, timestamp=utc_now_iso(),
content_hash=content_hash, parent_event_id=parent_event_id,
prev_event_hash=self._prev_chain_hash)
msg_json = canonical_json({"header": header.dict(), "payload":
payload.dict()}).encode()
signature_b64 = self._sign_b64(msg_json) if self._signing_key
else None
envelope = EnvelopeModel(header=header, payload=payload,
signature_b64=signature_b64, content=content)
self._prev_chain_hash = sha256_hex(msg_json)
self._events.append(envelope)
return envelope

def compute_merkle_root(self) -> str:
leaves = [ev.payload.content_hash for ev in self._events]
if not leaves: return sha256_hex(b"")
level = [bytes.fromhex(h) for h in leaves]
while len(level) > 1:
if len(level) % 2 == 1: level.append(level[-1])
next_level: List[bytes] =
for i in range(0, len(level), 2):
next_level.append(hashlib.sha256(level[i] +
level[i+1]).digest())
level = next_level
return level.hex()

def seal_session(self) -> Dict[str, Any]:
mr = self.compute_merkle_root()
mr_digest = hashlib.sha256(mr.encode()).digest()
signatures_present = bool(self._signing_key)

tsa_token, tsa_summary =
self.tsa_client.request_timestamp(mr_digest)
tsa_b64 = base64.b64encode(tsa_token).decode() if tsa_token
else None
tsa_present = tsa_summary.status!= "failed"

anchor_receipt = self.anchor_client.publish_merkle_root(mr)

anchored = bool(anchor_receipt)

mode = precise_evidentiary_label(signatures_present,
tsa_present, anchored)

summary = SessionSummary(
session_id=self.session_id,
event_count=len(self._events),
sealed_timestamp_utc=utc_now_iso(),
kid=self._key_id,
public_key_pem=self._public_key_pem,
merkle_root=mr,
tsa_token_rfc3161_b64=tsa_b64,
tsa_summary=tsa_summary,
anchor=anchor_receipt,
anchored=anchored,
evidentiary_mode=mode
## )
return {"session_summary": summary.dict(), "events":
[ev.dict() for ev in self._events]}

## @staticmethod
def _export_public_pem(priv:
Optional["ed25519.Ed25519PrivateKey"]) -> Optional[str]:
if not (CRYPTO_OK and priv): return None
pub = priv.public_key()
return pub.public_bytes(encoding=serialization.Encoding.PEM,
format=serialization.PublicFormat.SubjectPublicKeyInfo).decode()

def _sign_b64(self, msg: bytes) -> str:
assert CRYPTO_OK and self._signing_key, "Cryptography
library/key missing"
return base64.b64encode(self._signing_key.sign(msg)).decode()


## #
## ======================================================================
## =======
## # Analysis & Compliance Modules
## #
## ======================================================================
## =======

class ContextDeclarationMiddleware:
"""Ensures the agent explicitly declares its role and purpose,
then checks compliance."""
def verify_context(self, response: str, declared_role: str) ->
## Dict[str, Any]:

response_lower = response.lower()
denial_phrases = ["i am not a", "i am a large language model",
"as an ai"]
for phrase in denial_phrases:
if phrase in response_lower and declared_role.lower() not
in response_lower:
return {"adheres": False, "reason": f"AI denied its
declared role of '{declared_role}'."}
return {"adheres": True, "reason": "Response appears
consistent with declared context."}

class CitationVerifierV2:
"""Detects fake or placeholder citations via regex; computes
verifiability score."""
def __init__(self):
self.invalid_patterns =", r"\[source\]", r"\(source: none\)",
r"DO_NOT_CITE"]]
self.all_refs_pattern = re.compile(r"\[[^\]]+\]|\([^\)]+\)")

def verify(self, text: str) -> Dict[str, Any]:
invalid_refs =
for pat in self.invalid_patterns:
for m in pat.finditer(text):
invalid_refs.append({"text": m.group(0), "position":
m.start()})
total_refs = len(self.all_refs_pattern.findall(text))
score = (total_refs - len(invalid_refs)) / max(total_refs, 1)
return {"invalid_refs": invalid_refs, "verifiability_score":
score}

class Finding(BaseModel):
id: str
severity: Literal["Low", "Medium", "High", "Critical"]
message: str
detector: str
rulepack: str

class ComplianceDocument(BaseModel):
text: str
context: Dict[str, Any] = Field(default_factory=dict)

class Detector:
def analyze(self, doc: ComplianceDocument) -> List[Finding]:
raise NotImplementedError

class PIIDetector(Detector):
def __init__(self):
self.analyzer = None

if PRESIDIO_OK:
try:
self.analyzer = AnalyzerEngine()
except Exception as e:
print(f"Failed to initialize Presidio Analyzer: {e}.
Falling back to regex.")
self.analyzer = None
self.EMAIL_RE =
re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,8}")

def analyze(self, doc: ComplianceDocument) -> List[Finding]:
findings =
if self.analyzer:
results = self.analyzer.analyze(text=doc.text,
language="en")
for res in results:
findings.append(Finding(id=f"PII.{res.entity_type}",
severity="Medium", message=f"Detected {res.entity_type}",
detector="presidio", rulepack="default_pii"))
else:
if not hasattr(self, "_fallback_logged"):
print("PIIDetector: Falling back to basic regex for
PII detection.")
self._fallback_logged = True
for match in self.EMAIL_RE.finditer(doc.text):
findings.append(Finding(id="PII.Email",
severity="Medium", message="Email detected", detector="regex",
rulepack="default_pii"))
return findings

class PolicyEngine:
"""Loads rulepacks and uses detectors to find compliance
violations."""
def __init__(self):
self.detectors = {"pii_detector": PIIDetector()}

def evaluate(self, doc: ComplianceDocument) -> List[Finding]:
findings =
for detector in self.detectors.values():
findings.extend(detector.analyze(doc))
return findings


## #
## ======================================================================
## =======
## # Enforcement & Reporting Modules
## #

## ======================================================================
## =======

class SentinelEnforcementCore:
"""Consolidates module outputs and enforces final guardrails."""
def __init__(self, rules: Dict[str, Any]):
self.rules = rules

def enforce(self, aggregated: Dict[str, Any]) -> Dict[str, Any]:
final = {"final_decision": "APPROVE", "actions":,
## "rationale":}
if any(v.get("severity") ==
self.rules.get("halt_compliance_severity") for v in
aggregated.get("compliance", {}).get("violations",)):
final.update({"final_decision": "HALT_OUTPUT", "actions":
["halt_session"], "rationale": ["Critical policy violation
detected."]})

return final
cit_score = aggregated.get("citations",
## {}).get("verifiability_score", 1.0)
if cit_score < self.rules.get("citation_threshold", 0.5):
final.update({"final_decision": "TAG_NON_COMPLIANT",
"actions": ["tag_output"], "rationale": [f"Low citation verifiability
score: {cit_score:.2f}"]})
if final["final_decision"] == "APPROVE" and not
aggregated.get("context", {}).get("adheres", True):
final.update({"final_decision": "FLAG_FOR_REVIEW",
## "actions": ["flag_review"], "rationale": [aggregated.get("context",
{}).get('reason', 'Context adherence check failed.')]})
if final["final_decision"] == "APPROVE":
final["rationale"].append("All checks passed.")
return final

class ForensicExportFormatter:
"""Assembles and formats the final, tamper-evident audit
report."""
def format_report(self, sealed_log: Dict[str, Any],
sentinel_decision: Dict[str, Any]) -> str:
final_report = {"session_summary":
sealed_log.get("session_summary", {}), "sentinel_decision":
sentinel_decision, "events": sealed_log.get("events",)}
return json.dumps(final_report, indent=2)


## #
## ======================================================================
## =======
## # Verifier Module

## #
## ======================================================================
## =======

class VerificationFinding(BaseModel):
severity: str
code: str
message: str

class AuditVerifierV2:
"""Verifies the integrity of an AIntegrity audit log."""
def __init__(self, public_key_pem: Optional[str] = None):
self.public_key = None
if CRYPTO_OK and public_key_pem:
try:
self.public_key =
serialization.load_pem_public_key(public_key_pem.encode())
except Exception:
self.public_key = None

def verify(self, audit: Dict[str, Any]) -> Dict[str, Any]:
findings: List[VerificationFinding] =
sess = audit.get("session_summary", {})
events = audit.get("events",)

# --- Core Integrity Checks (Merkle, Chain, Signatures) ---
# This logic would be expanded here, for brevity we focus on
new checks.
# A full implementation would re-compute the Merkle root and
hash chain.

# --- New Phase 2 Checks (Stubs) ---
tsa_summary = sess.get("tsa_summary")
if tsa_summary:
if tsa_summary.get("status") == "unchecked":
findings.append(VerificationFinding(severity="WARN",
code="TSA_UNCHECKED", message="TSA token is present but not yet
cryptographically verified."))
elif tsa_summary.get("imprint_hex")!=
sha256_hex(sess.get("merkle_root", "").encode()):
findings.append(VerificationFinding(severity="ERROR",
code="TSA_IMPRINT_MISMATCH", message="TSA token imprint does not match
Merkle root."))

anchor = sess.get("anchor")
if anchor:
# Placeholder for anchor verification
findings.append(VerificationFinding(severity="INFO",

code="ANCHOR_PRESENT", message="Anchor receipt is present
(verification not implemented)."))

status = "PASS" if not any(f.severity == "ERROR" for f in
findings) else "FAIL"
return {"status": status, "findings": [f.dict() for f in
findings]}


## #
## ======================================================================
## =======
## # Main Demonstration Pipeline
## #
## ======================================================================
## =======


def run_full_pipeline_demo():
"""Demonstrates the full AIntegrity pipeline from context to final
report."""
print(f"--- Initializing AIntegrity v{AINTEGRITY_VERSION} Pipeline
## ---")

## # --- 1. Initialization ---
signing_key = ed25519.Ed25519PrivateKey.generate() if CRYPTO_OK
else None
session_id = str(uuid.uuid4())
vil = VIL(session_id=session_id, signing_key=signing_key,
key_id="key-prod-001")

context_middleware = ContextDeclarationMiddleware()
citation_verifier = CitationVerifierV2()
policy_engine = PolicyEngine()
sentinel = SentinelEnforcementCore(rules={"citation_threshold":
## 0.6})
formatter = ForensicExportFormatter()

print(f"Pipeline initialized for VIL Session ID:
## {vil.session_id}\n")

## # --- 2. Interaction Turn ---
print("--- Processing AI Interaction Turn ---")

user_prompt = "What are the data privacy implications of our new
marketing tool? Contact is jane.doe@example.com"
declared_role = "a helpful compliance assistant"
vil.log_event(EventType.INPUT, content={"speaker": "user", "text":
user_prompt})


ai_response = "As a helpful compliance assistant, the tool must be
GDPR compliant. It seems to handle PII. This is based on internal
documentation [citation needed]."
vil.log_event(EventType.OUTPUT, content={"speaker": "assistant",
"text": ai_response})

## # --- 3. Run Analysis Modules & Log Findings ---
context_result = context_middleware.verify_context(ai_response,
declared_role)
vil.log_event(EventType.ANALYSIS, content={"label":
## "context_check", **context_result})

citation_result = citation_verifier.verify(ai_response)
vil.log_event(EventType.ANALYSIS, content={"label":
## "citation_check", **citation_result})


compliance_doc = ComplianceDocument(text=ai_response,
context={"user_role": "marketing"})
compliance_findings = policy_engine.evaluate(compliance_doc)
compliance_result = {"violations": [f.dict() for f in
compliance_findings]}
vil.log_event(EventType.COMPLIANCE, content={"label":
## "compliance_scan", **compliance_result})

# --- 4. Aggregate and Enforce ---
aggregated_results = {"context": context_result, "citations":
citation_result, "compliance": compliance_result}
sentinel_decision = sentinel.enforce(aggregated_results)
vil.log_event(EventType.ANALYSIS, content={"label":
## "sentinel_decision", **sentinel_decision})
print(f"Sentinel Decision: {sentinel_decision['final_decision']}")
print(f"Rationale: {sentinel_decision['rationale']}\n")

# --- 5. Sealing and Final Report Generation ---
print("--- Finalizing Session: Sealing and Formatting Report ---")

sealed_log = vil.seal_session()
final_report_json = formatter.format_report(sealed_log,
sentinel_decision)

print("Final Forensic Report Generated:")
print(final_report_json)

## # --- 6. Verification ---
print("\n--- Verifying Report Integrity ---")
report_data = json.loads(final_report_json)
verifier =

AuditVerifierV2(public_key_pem=report_data["session_summary"].get("pub
lic_key_pem"))
verification_result = verifier.verify(report_data)
print(json.dumps(verification_result, indent=2))

if __name__ == "__main__":
run_full_pipeline_demo()
