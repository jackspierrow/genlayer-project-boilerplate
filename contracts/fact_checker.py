# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
from genlayer import *


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
                response_format="json"
            )

            if not isinstance(result, dict):
                raise gl.UserError("Invalid LLM response")

            if result.get("verdict") not in (
                "Supported",
                "Not Supported",
                "Unclear",
            ):
                raise gl.UserError("Invalid verdict")

            return {
                "claim": claim,
                "verdict": result["verdict"],
                "reason": str(result.get("reason", "")),
            }

        def validator_fn(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False

            try:
                leader_data = leader_result.calldata

                if not isinstance(leader_data, dict):
                    return False

                if leader_data.get("verdict") not in (
                    "Supported",
                    "Not Supported",
                    "Unclear",
                ):
                    return False

                own_result = leader_fn()

                return (
                    own_result["verdict"]
                    == leader_data["verdict"]
                )

            except Exception:
                return False

        result = gl.vm.run_nondet_unsafe(
            leader_fn,
            validator_fn
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
