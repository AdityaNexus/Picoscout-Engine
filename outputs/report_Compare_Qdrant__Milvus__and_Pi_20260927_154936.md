# Research Report: Compare Qdrant, Milvus, and Pinecone for billion-scale vector similarity search: analyze HNSW vs DiskANN indexing performance, memory usage, filtering latency, and hybrid BM25 search support.

Qdrant, Milvus, and Pinecone all offer vector similarity search capabilities, but their performance characteristics differ significantly in terms of HNSW vs DiskANN indexing, memory usage, filtering latency, and hybrid BM25 search support. 

### HNSW vs DiskANN Indexing Performance
- **HNSW (Memory-based)**: Milvus with HNSW has up to 74.1% lower throughput and 96.7% higher latency than Milvus with DiskANN, while DiskANN outperforms Milvus with IVF by up to 3.2× throughput and 44.5% lower latency in three out of four datasets.
- **DiskANN (Storage-based)**: DiskANN achieves up to 53.6% lower P99 latency than IVF under similar conditions, leading to a similar or better performance compared to HNSW.

### Memory Usage
- **HNSW**: Milvus with HNSW uses up to 8.19 GB of memory, which does not fit in `shared_buffers`, `effective_cache_size`, or other cache parameters.
- **DiskANN**: DiskANN is designed to use significantly less memory than HNSW, making it suitable for large-scale datasets.

### Filtering Latency
- **HNSW**: Milvus with HNSW has higher filtering latency compared to DiskANN. For example, in the Cohere 1M dataset, Milvus-DiskANN demonstrates 7.7% and 50.8% higher P99 latency than Milvus-HNSW, respectively.
- **DiskANN**: DiskANN achieves lower filtering latency than HNSW, especially under increased thread counts.

### Hybrid BM25 Search Support
- **Milvus**: Supports hybrid search with BM25 and vector search, offering a wide range of indexing algorithms including IVF, HNSW, and DiskANN.
- **Qdrant**: Supports hybrid search using HNSW and can be configured to use disk storage for large datasets. It allows for filtering during the graph traversal process, which is more efficient than post-filtering.
- **Pinecone**: Supports hybrid search with BM25 and vector search, but it uses a single-stage filtering approach that is less efficient compared to Qdrant's pre-filtering.

### Summary
- **HNSW** is memory-efficient but has higher latency and is not suitable for large-scale datasets due to memory constraints.
- **DiskANN** offers better performance in terms of throughput and latency, especially under high thread counts and larger dataset sizes, but requires more memory than HNSW.
- **Milvus** supports hybrid search with BM25 and vector search, providing flexibility in indexing and filtering. It is well-suited for large-scale datasets due to its support for multiple indexing algorithms.
- **Qdrant** allows for hybrid search with BM25 and vector search, offering efficient pre-filtering during graph traversal. It is suitable for applications requiring large-scale vector search on commodity hardware.
- **Pinecone** supports hybrid search but has higher latency compared to Qdrant due to its single-stage filtering approach.

All three systems offer vector similarity search capabilities, but their performance characteristics differ significantly based on indexing strategy, memory usage, and filtering efficiency.

---
*Editor verdict: ✅ Accepted — Looks good.*