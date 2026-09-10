# Local Audit Report — ratiss-topological-decoherence-engine

> Scope: local clone only. No remote repository was modified and no push was performed.

## Repository Structure

| Check | Result |
|---|---|
| Tracked/local file count | 116 |
| Python file count | 24 |
| README | PASS |
| RATISS Labs logo (`docs/assets/logo.png`) | PASS |
| Apache 2.0 LICENSE | PASS |
| `CITATION.cff` | PASS |

## Test Validation

- Command: `python3 -m pytest -v`
- Exit status: `0`

```text
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/ubuntu/ratiss-labs-repos/ratiss-topological-decoherence-engine
configfile: pyproject.toml
testpaths: tests
plugins: anyio-4.14.2
collected 16 items

tests/test_cloud_server.py .                                             [  6%]
tests/test_external_statevector.py .                                     [ 12%]
tests/test_logical_qubit.py ..                                           [ 25%]
tests/test_perceval_direct.py s                                          [ 31%]
tests/test_photonic_and_bio.py ..                                        [ 43%]
tests/test_pipeline.py .                                                 [ 50%]
tests/test_qiskit_counts.py .                                            [ 56%]
tests/test_studio_import.py ..                                           [ 68%]
tests/test_topology.py .                                                 [ 75%]
tests/test_tsp.py .                                                      [ 81%]
tests/test_ttf_ablation_cli.py .                                         [ 87%]
tests/test_ttf_stabilization.py ..                                       [100%]

======================== 15 passed, 1 skipped in 3.51s =========================

```

## Compliance Notes

- Branding and common repository metadata were applied locally.
- Scientific claims were not upgraded from proxy evidence to full validation.
- The three required technical Bible documents were not present in the supplied workspace.
- This report is an engineering audit snapshot, not a claim of zero defects.
