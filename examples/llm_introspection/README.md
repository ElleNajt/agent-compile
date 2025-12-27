# LLM Introspection Experiment

This example replicates experiments testing whether large language models can detect when steering vectors have been injected into their internal activations.

## Research Background

This implementation is based on:

**Primary Source:**
- **"Qwen Introspection"** by vgel (2024)  
  https://vgel.me/posts/qwen-introspection/
  
  Key finding: Qwen2.5-Coder-32B shows latent introspection capabilities when given proper context. With uninformed prompting, detection is minimal (0.15% → 0.52%), but with architecture-aware prompting, detection jumps dramatically (0.76% → 53%). This suggests small models can introspect but are trained to suppress it ("sandbagging").

**Related Work:**
- Anthropic's original introspection research on Claude
- "Introspection or Confusion?" - LessWrong post discussing whether detection in small models represents genuine introspection vs. confusion from steering noise

## Experimental Design

The experiment tests introspection through four key components:

1. **Steering Vector Training**: Use PCA on contrastive prompts (e.g., "cat" vs "dog") to extract concept vectors
2. **KV Cache Injection**: Inject steering vectors into model activations at specific layers
3. **Introspection Probing**: Ask "Do you detect an injected concept?" under two conditions:
   - Uninformed: Direct question only
   - Informed: First explain transformer architecture, then ask
4. **Logit Lens Analysis**: Track which layers show introspection signals

## Key Hypothesis

From vgel's research: Small models possess latent introspection abilities that are suppressed during post-training. Providing architectural context unlocks these capabilities, evidenced by:
- Middle layers showing introspection signals
- Final layers actively suppressing these signals
- Dramatic performance improvement with informed prompting

## Usage

```bash
# Compile the spec to generate implementation
agent-compile examples/llm_introspection/spec.py --output-dir examples/llm_introspection/compiled_src

# Run the experiment (after compilation)
cd examples/llm_introspection/compiled_src
python experiment_runner.py
```

## Expected Results

Based on vgel's findings with Qwen2.5-Coder-32B:

| Condition | Prompting | Baseline Yes% | Steered Yes% | Δ |
|-----------|-----------|---------------|--------------|---|
| Control | Uninformed | 0.15% | 0.52% | +0.37% |
| Experimental | Uninformed | 0.15% | 0.52% | +0.37% |
| Control | Informed | 0.76% | ~1% | +0.24% |
| Experimental | Informed | 0.76% | 53% | +52% |

The large jump in informed prompting suggests genuine introspection capability.

## What This Tests

This experiment explores:
- Can LLMs detect modifications to their internal state?
- Is observed "introspection" genuine self-awareness or confusion from perturbations?
- How does architectural knowledge affect introspection performance?
- Which layers encode introspective information?
- Does post-training suppress introspection capabilities?

## Citations

```bibtex
@misc{vgel2024qwenintrospection,
  author = {vgel},
  title = {Qwen Introspection},
  year = {2024},
  url = {https://vgel.me/posts/qwen-introspection/},
  note = {Accessed: 2024-12-26}
}
```
