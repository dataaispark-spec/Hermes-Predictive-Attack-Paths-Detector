# Temporal starter — AttackPathPipeline

Part of **[Hermes-Predictive-Attack-Paths-Detector](https://github.com/dataaispark-spec/Hermes-Predictive-Attack-Paths-Detector)**.

## Purpose

Durable workflow: collect (synthetic) → score path → **wait for human approval signal** → optional downstream action.

## Run (lab)

```bash
cd deploy && docker compose -f docker-compose.temporal.yml up -d && cd ..
pip install -r temporal/requirements.txt
export PYTHONPATH=$(pwd)   # repo root: Hermes-Predictive-Attack-Paths-Detector
python temporal/worker.py
# other terminal:
python temporal/scripts/start_pipeline.py --wait-hours 0.01
python temporal/scripts/signal_approve.py --workflow-id <id>
```

See [docs/TEMPORAL.md](../docs/TEMPORAL.md).
