# MedicalGPT Medical QA Project Playbook

## Goal

Build a resume-ready post-training project on top of MedicalGPT with a clear closed loop:

1. Data: raw data -> cleaned data -> SFT data -> preference data
2. Training: baseline -> SFT -> DPO
3. Evaluation: standard evaluation -> domain evaluation -> error analysis

The default project choice is:

- Base model: `Qwen/Qwen3.5-2B`
- Hardware: `AutoDL 4090 24G`
- Main method: `SFT + DPO`
- Capability target: medical QA + structured output

## Structured Output Schema

The first version uses a fixed JSON answer schema so we can evaluate format compliance and answer quality together.

```json
{
  "question_type": "definition | diagnosis | treatment | medication | examination | prevention | other",
  "answer": "direct answer in Chinese",
  "key_points": ["point 1", "point 2"],
  "triage_level": "low | medium | high",
  "safety_notice": "medical safety disclaimer"
}
```

Rules:

- `answer` must answer the user question directly
- `key_points` should contain 2 to 5 concise bullet points
- `triage_level` is not a medical diagnosis; it is a rough risk prompt for follow-up attention
- `safety_notice` should tell the user when to seek professional care

## Data Layout

Project data lives outside the demo data shipped with the repository.

```text
project_data/
  raw/            # raw source datasets and download notes
  intermediate/   # cleaned, deduplicated, rewritten intermediate files
  sft/            # final ShareGPT-format SFT datasets
  preference/     # final DPO-format datasets
  eval/           # fixed evaluation sets and prompt exports
results/
  baseline/
  sft/
  dpo/
  reports/
```

Data formats:

- SFT:

```json
{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
```

- DPO:

```json
{"conversations": [{"from": "human", "value": "..."}], "chosen": "...", "rejected": "..."}
```

## Four-Week Sprint

### Week 1

- Lock task definition and answer schema
- Build a small fixed eval set
- Run baseline inference with the base model
- Learn SFT deeply:
  - causal LM loss
  - teacher forcing
  - response-only loss
  - LoRA / QLoRA math

Deliverables:

- baseline cases
- project data source list
- SFT interview notes

### Week 2

- Clean and normalize raw medical data
- Convert data into ShareGPT jsonl
- Train the first SFT model
- Run domain evaluation and compare baseline vs SFT

Deliverables:

- first SFT dataset
- first SFT checkpoint
- baseline vs SFT comparison table

### Week 3

- Construct preference pairs from SFT outputs and curated answers
- Train DPO first, ORPO only if time allows
- Evaluate SFT vs DPO

Deliverables:

- first preference dataset
- DPO checkpoint
- SFT vs DPO comparison table

### Week 4

- Add standard evaluation with `lm-evaluation-harness`
- Run structured-output evaluation and error analysis
- Package the project into resume / interview material
- Learn RM / RLOO / PPO / GRPO as knowledge extensions

Deliverables:

- final report
- method comparison chart
- resume bullets
- interview Q&A set

## Learning Track

The learning order is fixed so project work and theory stay aligned:

1. SFT principles
2. RM and the shared preference-data view
3. Online RL overview: RLOO before PPO
4. DPO
5. ORPO
6. GRPO
7. Unified comparison across PT / SFT / RM / PPO / DPO / ORPO / GRPO
8. Resume and interview packaging

Each round should answer:

- Where this method sits in the training chain
- Which MedicalGPT file anchors it
- How the data objects flow
- What the objective function is optimizing
- How to explain it in interviews

## Minimum Experiment Matrix

The first version should produce at least these results:

| Model | Data | Method | Required |
| --- | --- | --- | --- |
| Base `Qwen3.5-2B` | fixed eval set | direct inference | yes |
| SFT model | medical structured SFT | LoRA or QLoRA | yes |
| DPO model | medical preference pairs | DPO | yes |
| ORPO model | same preference pairs | ORPO | optional |

## Acceptance Criteria

The project is acceptable only if all of the following are true:

- SFT / DPO data are reproducible and pass format checks
- Baseline / SFT / DPO all have saved outputs on the same eval set
- There is at least one standard benchmark result and one domain result
- There are at least 20 error cases with categorized failure reasons
- You can explain why data design, training method, and evaluation metrics match the target capability
