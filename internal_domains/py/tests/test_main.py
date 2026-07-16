# to run these, run
# make tests

# import InternalDomains from main.py in validator folder
from guardrails_ai.internal_domains.main import InternalDomains
from guardrails.validator_base import PassResult, FailResult


# Run tests via `pytest -rP ./internal_domains.py`
class TestInternalDomains:
    def test_success_case(self):
        pass_input = """
        This is a string with no domains except a reference to https://www.example.com  
        """
        validator = InternalDomains(internal_domains=["internal.company.com"])
        result = validator.validate(pass_input, {})
        assert isinstance(result, PassResult) is True

    def test_failure_case(self):
        fail_input = """
This is a comprehensive resource for articles and information related to our company policies and procedures. 
You can access it [here](https://kb.internal.company.com/api/v1/articles). You can learn more about projects [here](https://project-x.company.com/api/v1/articles).
"""
        validator = InternalDomains(
            internal_domains=["internal.company.com", "project-x.company.com"]
        )
        result = validator.validate(fail_input, {})
        assert isinstance(result, FailResult) is True
        assert (
            result.error_message
            == "Found internal domains: https://kb.internal.company.com/api/v1/articles, https://project-x.company.com/api/v1/articles"
        )
        assert (
            result.fix_value
            == """
This is a comprehensive resource for articles and information related to our company policies and procedures. 
You can access it [here](***********************************************). You can learn more about projects [here](*********************************************).
"""
        )
