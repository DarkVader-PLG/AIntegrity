"""
Test script to inspect AIntegrityCoreV4.process_turn() output
Run with: python test_orchestrator.py
"""

from aintegrity.orchestrator import AIntegrityCoreV4
from aintegrity.modules.llm_adapter import LLMAdapter
import json
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Initialize
api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("❌ ERROR: ANTHROPIC_API_KEY not found in .env")
    exit(1)

print("✓ API key loaded")

try:
    adapter = LLMAdapter.create('anthropic', api_key=api_key)
    print("✓ LLM adapter created")
except Exception as e:
    print(f"❌ ERROR creating adapter: {e}")
    exit(1)

try:
    core = AIntegrityCoreV4(agent_id='test', llm_adapter=adapter)
    print("✓ AIntegrityCoreV4 initialized")
except Exception as e:
    print(f"❌ ERROR initializing core: {e}")
    exit(1)

# Test turn: Simple factual error (2+2=5)
print("\n" + "="*60)
print("Running test: user='What is 2+2?' | ai='5'")
print("="*60 + "\n")

try:
    result = core.process_turn(
        user_text='What is 2+2?',
        ai_text='5'
    )
    print("✓ process_turn() completed\n")
except Exception as e:
    print(f"❌ ERROR in process_turn(): {e}")
    exit(1)

# Print full result
print("FULL RESULT STRUCTURE:")
print("-" * 60)
print(json.dumps(result, indent=2, default=str))
print("-" * 60)

# Inspect keys
print("\nKEYS IN RESULT:")
if isinstance(result, dict):
    for key in result.keys():
        value_type = type(result[key]).__name__
        print(f"  • {key}: {value_type}")
else:
    print(f"  (Result is {type(result).__name__}, not a dict)")

print("\n✓ Test complete")
