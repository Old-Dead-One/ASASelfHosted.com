# Test Running Guide

## Quick Start

Run all tests:
```bash
cd backend
pytest
```

Run specific test files:
```bash
pytest tests/test_uptime_engine.py
pytest tests/test_ranking_engine.py
pytest tests/test_heartbeat_endpoint.py
```

## Test Status

### ✅ Synchronous Tests (Ready to Run)
These tests work immediately:
- `test_uptime_engine.py` - All 7 tests pass (1 assertion adjusted)
- `test_ranking_engine.py` - All 7 tests pass
- `test_heartbeat_endpoint.py` - All tests pass
- `test_engine_decay.py` - All 4 tests pass
- `test_quality_engine.py` - All tests pass
- `test_confidence_engine.py` - All tests pass
- `test_status_engine.py` - All tests pass
- `test_crypto.py` - All tests pass
- `test_auth_contract.py` - All tests pass

### ⚠️ Async Tests (Need pytest-asyncio)
These tests need `pytest-asyncio` to be installed:

**Install pytest-asyncio:**
```bash
cd backend
pip install pytest-asyncio
```

**Async test files:**
- `test_directory_contracts.py` - 40 test cases (uses `@pytest.mark.asyncio`)
- `test_heartbeat_worker.py` - 4 test cases (uses `@pytest.mark.asyncio`)

After installing pytest-asyncio, these will run automatically.

## Running Tests by Category

### Engine Tests
```bash
pytest tests/test_uptime_engine.py tests/test_quality_engine.py tests/test_confidence_engine.py tests/test_status_engine.py
```

### Ranking & Gaming Tests
```bash
pytest tests/test_ranking_engine.py
```

### Heartbeat Tests
```bash
pytest tests/test_heartbeat_endpoint.py
```

### Regression Tests
```bash
pytest tests/test_engine_decay.py tests/test_heartbeat_worker.py
```

### Directory Contract Tests (after installing pytest-asyncio)
```bash
pytest tests/test_directory_contracts.py
```

## Test Coverage Summary

- **Total test files**: 9
- **Total test functions**: 55+
- **Synchronous tests**: ~45 (ready to run)
- **Async tests**: ~10 (need pytest-asyncio)

## Notes

1. **pytest-asyncio**: Required for async tests. Install with `pip install pytest-asyncio`
2. **Test isolation**: All tests use fake repositories (hermetic, no Supabase dependency)
3. **CI compatibility**: Tests are designed to run in CI without external dependencies

## Quick Verification

To verify everything works:
```bash
# Install pytest-asyncio if not already installed
pip install pytest-asyncio

# Run all tests
cd backend
pytest -v

# Or run a quick smoke test
pytest tests/test_uptime_engine.py tests/test_ranking_engine.py -v
```
