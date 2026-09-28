def test_fact_checker_contract(direct_vm, direct_deploy, direct_alice):
    contract = direct_deploy("contracts/fact_checker.py")
    direct_vm.sender = direct_alice

    contract.last_claim = "test"
    contract.last_verdict = "Supported"
    contract.last_reason = "Test reason"

    result = contract.get_result()

    assert result["claim"] == "test"
    assert result["verdict"] == "Supported"
    assert result["reason"] == "Test reason"
