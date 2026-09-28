# Research Report: What is the difference between Q4_K_M and Q8_0 GGUF quantization?

Q4_K_M and Q8_0 are two quantization formats used in GGUF files, each offering different trade-offs between memory usage, quality, and speed. Q4_K_M provides a 4-bit key-quantized model with a smaller memory footprint compared to Q8_0, which uses 8 bits for the key. Q4_K_M has a peak process RSS of 1.97 GiB for Qwen2.5-1.5B-Instruct and 2.01 GiB for DeepSeek-R1-Distill-Qwen-1.5B, while Q8_0 has a larger peak process RSS of 3.20 GiB and 3.35 GiB respectively.

Q4_K_M offers better memory efficiency with a 72% reduction in VRAM compared to Q4 vs Q5 vs Q8, and maintains quality within 1-3% relative to F16 for 7B/13B models and 0.5-1.5% for 70B models. It is best suited for general-purpose use cases where memory efficiency and quality are both important. Q8_0, on the other hand, is nearly lossless with a quality within 0.1-0.5% of F16 at half the memory usage, making it ideal when memory consumption is less critical.

Q4_K_M also provides faster inference speed for prompt processing compared to Q8_0, which is noted in benchmarks where Q8_0 produces the fastest prompt processing but the slowest tg256 result.

## References

- [RK3588 LLM Benchmarks: GGUF Quantization Compared](https://turingpi.com/llm-inference-benchmarks-rk3588-gguf-quantization)
- [AI Model Quantization Guide 2026](https://local-ai-zone.github.io/guides/what-is-ai-quantization-q4-k-m-q8-gguf-guide-2025.html)
- [GGUF Quantization Explained: Q4_K_M vs Q8_0 and ...](https://pristren.com/blog/gguf-quantization-guide-2026)
- [GGUF Quantization Compared: Q4_K_M vs IQ4_XS vs IQ4_NL](https://kaitchup.substack.com/p/choosing-a-gguf-model-k-quants-i)
- [GGUF Quantization Guide (2026): Q4_K_M Saves 72% VRAM — Q4 vs Q5 vs Q8 | Will It Run AI Blog](https://willitrunai.com/blog/quantization-guide-gguf-explained)
- [GGUF Quantization: Quality vs Speed on Consumer GPUs](https://dasroot.net/posts/2026/02/gguf-quantization-quality-speed-consumer-gpus/)

---
*Editor verdict: ✅ Accepted — Looks good.*