import json


def test_fact_checker_contract(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice

    direct_vm.mock_web(
        r".*google\.com/search.*",
        {"status": 200, "body": "Bitcoin was created in 2009 by Satoshi Nakamoto."},
    )

    direct_vm.mock_llm(
        r".*You are a fact-checking assistant.*",
        json.dumps({
            "verdict": "Supported",
            "reason": "The available information supports the claim."
        }),
    )

    contract = direct_deploy("contracts/fact_checker.py")

    contract.verify_claim("Bitcoin was created in 2009.")

    result = contract.get_result()

    assert result["claim"] == "Bitcoin was created in 2009."
    assert result["verdict"] == "Supported"
    assert result["reason"] == "The available information supports the claim."
