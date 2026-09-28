# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *
import genlayer.gl.vm as glvm


class FactChecker(gl.Contract):
    last_claim: str
    last_verdict: str
    last_reason: str

    @gl.public.write
    def verify_claim(self, claim: str) -> None:

        def leader_fn():
            web_data = gl.nondet.web.render(
                "https://www.google.com/search?q=" + claim.replace(" ", "+"),
                mode="text",
            )

            prompt = f"""
You are a fact-checking assistant.

Claim:
{claim}

Web information:
{web_data}

Evaluate whether the claim is supported by the available information.

Return JSON with exactly these fields:
{{
    "verdict": "Supported" or "Not Supported" or "Unclear",
    "reason": "brief explanation"
}}
"""

            result = gl.nondet.exec_prompt(
                prompt,
                response_format="json",
            )

            if not isinstance(result, dict):
                raise Exception("Invalid LLM response")

            verdict = result.get("verdict")

            if verdict not in (
                "Supported",
                "Not Supported",
                "Unclear",
            ):
                raise Exception("Invalid verdict")

            return {
                "claim": claim,
                "verdict": verdict,
                "reason": str(result.get("reason", "")),
            }

        def validator_fn(leader_result):
            if not isinstance(leader_result, glvm.Return):
                return False

            try:
                data = leader_result.calldata

                return (
                    isinstance(data, dict)
                    and data.get("verdict")
                    in (
                        "Supported",
                        "Not Supported",
                        "Unclear",
                    )
                )

            except Exception:
                return False

        result = glvm.run_nondet_unsafe(
            leader_fn,
            validator_fn,
        )

        self.last_claim = result["claim"]
        self.last_verdict = result["verdict"]
        self.last_reason = result["reason"]

    @gl.public.view
    def get_result(self) -> dict:
        return {
            "claim": self.last_claim,
            "verdict": self.last_verdict,
            "reason": self.last_reason,
        }
