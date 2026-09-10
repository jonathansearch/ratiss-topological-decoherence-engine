import json
from pathlib import Path

from ratiss_topological_decoherence.cli import main
from ratiss_topological_decoherence.simulation import run_local_demo


def test_cli_writes_two_separate_ttf_ablation_timelines(tmp_path, monkeypatch):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(run_local_demo()))
    destination = tmp_path / "scenarios"
    monkeypatch.setattr("sys.argv", ["ratiss-topo-demo", "--ttf-ablation-input", str(source), "--ttf-ablation-dir", str(destination)])
    main()
    baseline = json.loads((destination / "timeline_baseline.json").read_text())
    regularized = json.loads((destination / "timeline_regularized.json").read_text())
    assert baseline["provenance"]["mode"] == "ttf_smooth_baseline"
    assert regularized["provenance"]["mode"] == "ttf_smooth_correlation_regularization"
