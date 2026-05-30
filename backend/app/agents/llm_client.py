"""多模型适配管理器 — 统一 OpenAI 接口 + 重试 + 并发 + 降级"""

import asyncio
import logging
import time
from typing import Optional

from openai import APIError, APIConnectionError, RateLimitError, OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class LLMClientManager:
    """多模型适配管理器：重试、并发控制、故障降级、结构化日志"""

    def __init__(self):
        self._client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self._fallback_client: Optional[OpenAI] = None
        self._semaphore = asyncio.Semaphore(settings.llm_concurrency)

    def _get_fallback(self) -> OpenAI:
        if not self._fallback_client:
            self._fallback_client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=settings.llm_base_url,
            )
        return self._fallback_client

    async def complete(
        self,
        system_prompt: str,
        user_message: str,
        model: Optional[str] = None,
        response_format: Optional[dict] = None,
        tools: Optional[list] = None,
        tool_choice: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """统一的 LLM 调用接口，内置重试和降级"""
        last_error = None
        model = model or settings.llm_model
        max_tokens = max_tokens or settings.llm_max_tokens

        for attempt in range(3):
            try:
                async with self._semaphore:
                    start = time.time()
                    response = await asyncio.to_thread(
                        self._client.chat.completions.create,
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout=settings.llm_timeout,  # B1 fix: pass timeout
                        response_format=response_format,
                        tools=tools,
                        tool_choice=tool_choice,
                    )
                    latency = time.time() - start

                result = {
                    "content": response.choices[0].message.content or "",
                    "tool_calls": response.choices[0].message.tool_calls,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    },
                    "model": model,
                    "latency_ms": int(latency * 1000),
                }

                logger.info(
                    "llm_call_success",
                    extra={
                        "model": model,
                        "latency_ms": result["latency_ms"],
                        "tokens": result["usage"]["total_tokens"],
                        "attempt": attempt + 1,
                    },
                )
                return result

            except RateLimitError:
                wait = 2 ** attempt
                logger.warning("rate_limited", extra={"retry_in": wait, "attempt": attempt})
                await asyncio.sleep(wait)

            except (APIConnectionError, APIError, TimeoutError) as e:
                last_error = e
                logger.warning("llm_call_retry", extra={"attempt": attempt, "error": str(e)})
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)

        # 降级到备用模型
        logger.error("fallback_to_backup", extra={"error": str(last_error)})
        return await self._fallback_complete(system_prompt, user_message, max_tokens)

    async def _fallback_complete(
        self, system_prompt: str, user_message: str, max_tokens: int
    ) -> dict:
        try:
            client = self._get_fallback()
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=settings.llm_fallback_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            return {
                "content": response.choices[0].message.content or "",
                "tool_calls": None,
                "usage": {"total_tokens": 0},
                "model": settings.llm_fallback_model,
                "latency_ms": 0,
                "fallback": True,
            }
        except Exception as e:
            logger.error("fallback_failed", extra={"error": str(e)})
            return {
                "content": "抱歉，服务暂时不可用，请稍后再试。",
                "tool_calls": None,
                "usage": {"total_tokens": 0},
                "model": "fallback",
                "latency_ms": 0,
                "error": str(e),
            }


llm_client = LLMClientManager()
