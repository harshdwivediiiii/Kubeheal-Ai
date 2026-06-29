import os
from typing import Optional

from src.backend.core.config import settings


class LLMInference:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.llm_model

    def generate_fix_suggestion(
        self, error_log: str, context: Optional[str] = None
    ) -> str:
        prompt = f"""You are a Kubernetes SRE expert. Analyze this error and suggest a fix:

Error Log:
{error_log[:1000]}

Context:
{context if context else 'No additional context'}

Provide:
1. Root cause analysis
2. Immediate fix
3. Long-term prevention
"""
        return self._call_llm(prompt)

    def analyze_log_pattern(self, log_pattern: str) -> str:
        prompt = f"""Analyze this Kubernetes log pattern and identify the issue:

Log Pattern: {log_pattern[:500]}

Identify:
- The specific Kubernetes error
- Common causes
- Recommended actions
"""
        return self._call_llm(prompt)

    def _call_llm(self, prompt: str) -> str:
        if settings.openai_api_key:
            return self._call_openai(prompt)
        elif settings.anthropic_api_key:
            return self._call_anthropic(prompt)
        elif settings.groq_api_key:
            return self._call_groq(prompt)
        else:
            return self._rule_based_response(prompt)

    def _call_openai(self, prompt: str) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content

    def _call_anthropic(self, prompt: str) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _call_groq(self, prompt: str) -> str:
        from groq import Groq

        client = Groq(api_key=settings.groq_api_key)
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        return response.choices[0].message.content

    def _rule_based_response(self, prompt: str) -> str:
        if "OOMKilled" in prompt or "out of memory" in prompt.lower():
            return (
                "Root Cause: Container exceeded memory limit\n"
                "Immediate Fix: Increase memory limits or restart pod\n"
                "Prevention: Monitor memory usage and set appropriate resource limits"
            )
        elif "CrashLoopBackOff" in prompt:
            return (
                "Root Cause: Application crashing on startup\n"
                "Immediate Fix: Check application logs with 'kubectl logs --previous'\n"
                "Prevention: Add proper error handling and health checks"
            )
        elif "ImagePullBackOff" in prompt:
            return (
                "Root Cause: Container image not found or pull failed\n"
                "Immediate Fix: Verify image name and tag, check registry credentials\n"
                "Prevention: Use image tags, mirror images to local registry"
            )
        else:
            return (
                "Root Cause: Unknown failure pattern detected\n"
                "Immediate Fix: Check pod logs and events\n"
                "Prevention: Set up monitoring and alerting"
            )
