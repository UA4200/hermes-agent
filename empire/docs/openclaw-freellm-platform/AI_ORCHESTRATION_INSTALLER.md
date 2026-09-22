# OpenClaw Free LLM Platform — Workstream 9: AI Orchestration Installer

## Install

There is no package install step. `router_core` has zero required
third-party dependencies (stdlib only, by design) — copy
`empire/router_core/` into a project and `import router_core`.

## Verify

```bash
cd empire/router_core
python3 install_check.py
```

Real output from this session:
```
router_core install check
========================================
[OK] Python 3.12.10 >= 3.10
[OK] router_core imports cleanly
[OK] test suite: 18 passed in 0.12s
[INFO] optional dependency 'gptcache' not installed (router_core falls back to no-op — this is fine, not an error)
[INFO] optional dependency 'llmlingua' not installed (router_core falls back to no-op — this is fine, not an error)
========================================
PASS — router_core is importable and its test suite is green.
```

Exit code 0 = safe to import. The optional-dependency lines are
informational, not failures — `cache.py`/`compress.py` no-op cleanly
without them (Workstream 5).

## Optional: Real Caching/Compression

```bash
pip install gptcache llmlingua
```

Installing these does **not** automatically activate them — `router_core`
still returns `NoOpCache`/`NoOpCompressor` from `build_gptcache_backed_
cache()`/`build_llmlingua_backed_compressor()` until the real integration
is built out (explicitly deferred, see `cache.py`/`compress.py`'s
docstrings and `README.md`'s "What this does NOT do"). Detecting the
package is step one of a real integration, not the integration itself.

## Uninstall

Delete the `router_core/` directory. Nothing it does touches state
outside its own process (no files written outside `tests/`'s own
temp usage, no global config, no daemon).
