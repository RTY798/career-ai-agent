"""混合检索器 — BM25 关键词 + 向量语义双路召回 + RRF 融合"""

from typing import Optional

from rank_bm25 import BM25Okapi

from app.rag.vector_store import vector_store


class HybridRetriever:
    """混合检索：BM25 + 向量检索，RRF 加权融合"""

    def __init__(self):
        self._bm25_index: Optional[BM25Okapi] = None
        self._bm25_docs: list[str] = []

    def _build_bm25_index(self, docs: list[str]):
        """构建 BM25 索引"""
        tokenized = [self._tokenize(d) for d in docs]
        self._bm25_index = BM25Okapi(tokenized)
        self._bm25_docs = docs

    def _tokenize(self, text: str) -> list[str]:
        """中文 + 英文分词（对中文做字符级 + 英文做词级）"""
        import re

        tokens = []
        # 英文单词
        tokens.extend(re.findall(r"[a-zA-Z0-9_]+", text))
        # 中文单字（用字符保留语义单元）
        chinese_chars = re.findall(r"[一-鿿]", text)
        tokens.extend(chinese_chars)
        return tokens

    def retrieve(self, query: str, top_k: int = 5) -> list[dict]:
        """双路召回 → RRF 融合 → 返回 top_k"""
        # 1. 向量检索
        vector_results = vector_store.similarity_search(query, k=top_k * 2)

        # 2. BM25 检索（如果有索引）
        bm25_results = []
        if self._bm25_index:
            tokenized_query = self._tokenize(query)
            scores = self._bm25_index.get_scores(tokenized_query)
            # 取 top_k*2
            top_indices = sorted(
                range(len(scores)), key=lambda i: scores[i], reverse=True
            )[: top_k * 2]
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_results.append({
                        "content": self._bm25_docs[idx],
                        "metadata": {},
                        "score": float(scores[idx]),
                        "source": "bm25",
                    })

        # 3. 标记向量结果来源
        for r in vector_results:
            r["source"] = "vector"

        # 4. RRF 加权融合
        fused = self._reciprocal_rank_fusion(
            bm25_results, vector_results, k=60, weights=(0.3, 0.7)
        )

        # 5. 去重
        seen = set()
        unique = []
        for doc in fused:
            content = doc["content"][:100]  # 用前100字做去重key
            if content not in seen:
                seen.add(content)
                unique.append(doc)

        return unique[:top_k]

    def _reciprocal_rank_fusion(
        self,
        list1: list[dict],
        list2: list[dict],
        k: int = 60,
        weights: tuple[float, float] = (0.3, 0.7),
    ) -> list[dict]:
        """RRF 融合：score = w * 1/(k + rank)"""
        from collections import defaultdict

        rank_scores = defaultdict(float)

        for rank, doc in enumerate(list1):
            rank_scores[doc["content"]] += weights[0] / (k + rank + 1)

        for rank, doc in enumerate(list2):
            rank_scores[doc["content"]] += weights[1] / (k + rank + 1)

        sorted_docs = sorted(rank_scores.items(), key=lambda x: -x[1])

        seen_content = {d["content"] for d in list1 + list2}
        result = []
        for content, score in sorted_docs:
            # 从原结果中找到匹配项
            for d in list1 + list2:
                if d["content"] == content:
                    result.append({**d, "rrf_score": score})
                    break

        return result

    def rebuild_index(self, docs: list[str]):
        """重建 BM25 索引（知识库更新时调用）"""
        self._build_bm25_index(docs)


hybrid_retriever = HybridRetriever()
