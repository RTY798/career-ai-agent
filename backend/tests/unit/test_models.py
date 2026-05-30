"""TP1-2: Pydantic 校验边界值 (P0/smoke)"""

import pytest
from pydantic import ValidationError
from app.models.schemas import ChatRequest


class TestChatRequest:
    def test_valid_message(self):
        req = ChatRequest(message="hello")
        assert req.message == "hello"

    def test_empty_message_fails(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_whitespace_only_passes_validation(self):
        # Pydantic min_length checks length, not content; whitespace has length
        req = ChatRequest(message="   ")
        assert req.message == "   "

    def test_message_too_long_fails(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 2001)

    def test_message_exactly_2000_ok(self):
        req = ChatRequest(message="x" * 2000)
        assert len(req.message) == 2000

    def test_all_optionals_missing(self):
        req = ChatRequest(message="hello")
        assert req.resume is None
        assert req.jd is None
        assert req.conversation_id is None

    def test_resume_too_long_fails(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="hi", resume="x" * 50001)

    def test_resume_exactly_50000_ok(self):
        req = ChatRequest(message="hi", resume="x" * 50000)
        assert len(req.resume) == 50000

    def test_extra_fields_ignored(self):
        req = ChatRequest(message="hi", unknown_field="test")
        assert not hasattr(req, "unknown_field")
