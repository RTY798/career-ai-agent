"""TP1-4: HybridRetriever RRF 融合数学 + 分词 (P1)"""

import pytest
from app.rag.hybrid_retriever import HybridRetriever


class TestHybridRetriever:
    @pytest.fixture
    def retriever(self):
        return HybridRetriever()

    def test_tokenize_chinese(self, retriever):
        tokens = retriever._tokenize("你好世界")
        assert "你" in tokens
        assert "好" in tokens
        assert "世" in tokens
        assert "界" in tokens

    def test_tokenize_english(self, retriever):
        tokens = retriever._tokenize("hello world test")
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens

    def test_tokenize_mixed(self, retriever):
        tokens = retriever._tokenize("Python 是一种编程语言")
        assert "Python" in tokens
        assert "是" in tokens

    def test_tokenize_with_numbers(self, retriever):
        tokens = retriever._tokenize("Python3.12")
        assert "Python3" in tokens or "Python" in tokens

    def test_tokenize_empty(self, retriever):
        tokens = retriever._tokenize("")
        assert tokens == []

    def test_rrf_empty_lists(self, retriever):
        result = retriever._reciprocal_rank_fusion([], [])
        assert result == []

    def test_rrf_one_list_empty(self, retriever):
        list1 = [{"content": "doc1", "score": 1.0}]
        result = retriever._reciprocal_rank_fusion(list1, [])
        assert len(result) > 0

    def test_rrf_weights_affect_ranking(self, retriever):
        """验证权重变化影响排序"""
        list1 = [{"content": "A"}, {"content": "B"}]
        list2 = [{"content": "B"}, {"content": "C"}]

        result_a = retriever._reciprocal_rank_fusion(list1, list2, weights=(1.0, 0.0))
        result_b = retriever._reciprocal_rank_fusion(list1, list2, weights=(0.0, 1.0))

        assert result_a[0]["content"] == "A"
        assert result_b[0]["content"] == "B"

    def test_rrf_dedup(self, retriever):
        """去重"""
        docs = [
            {"content": "same content here " * 10},
            {"content": "same content here " * 10},
            {"content": "different content here " * 10},
        ]
        result = retriever._reciprocal_rank_fusion([docs[0]], [docs[1], docs[2]])
        contents = [r["content"] for r in result]
        assert contents.count(docs[0]["content"]) <= 1
