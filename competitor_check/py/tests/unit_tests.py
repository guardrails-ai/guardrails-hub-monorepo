from guardrails.validator_base import ErrorSpan
from guardrails_ai.competitor_check import CompetitorCheck


def test_filter_output_in_sentence():
    competitor_check = CompetitorCheck(competitors=[])
    assert competitor_check.filter_output_in_sentence("", []) == ""
    assert (
        competitor_check.filter_output_in_sentence("Apple", ["Apple"]) == "[COMPETITOR]"
    )
    assert (
        competitor_check.filter_output_in_sentence(
            "Apple is a great company", ["Apple"]
        )
        == "[COMPETITOR] is a great company"
    )
    assert (
        competitor_check.filter_output_in_sentence(
            "Banana is a great company", ["Apple"]
        )
        == "Banana is a great company"
    )


def test_compute_filtered_output():
    competitor_check = CompetitorCheck(competitors=[])
    assert competitor_check.compute_filtered_output([""], [[]]) == ""
    assert (
        competitor_check.compute_filtered_output(["Apple"], [["Apple"]])
        == "[COMPETITOR]"
    )
    assert (
        competitor_check.compute_filtered_output(
            ["Apple is a great company"], [["Apple"]]
        )
        == "[COMPETITOR] is a great company"
    )
    assert (
        competitor_check.compute_filtered_output(
            ["Banana is a great company"], [["Apple"]]
        )
        == "Banana is a great company"
    )
    assert (
        competitor_check.compute_filtered_output(
            ["Apple is a great company", "Banana is a great company"], [["Apple"], []]
        )
        == "[COMPETITOR] is a great companyBanana is a great company"
    )
    assert (
        competitor_check.compute_filtered_output(
            ["Apple is a great Apple company", "Banana is a great company"],
            [["Apple"], []],
        )
        == "[COMPETITOR] is a great [COMPETITOR] companyBanana is a great company"
    )


def test_compute_error_spans():
    competitor_check = CompetitorCheck(competitors=[])
    assert competitor_check.compute_error_spans([""], [[]]) == []

    assert compare_error_spans_lists(
        span_list1=competitor_check.compute_error_spans(["Apple"], [["Apple"]]),
        span_list2=[ErrorSpan(start=0, end=5, reason="Competitor was found: Apple")],
    )

    assert compare_error_spans_lists(
        span_list1=competitor_check.compute_error_spans(
            ["Apple is a great company"], [["Apple"]]
        ),
        span_list2=[ErrorSpan(start=0, end=5, reason="Competitor was found: Apple")],
    )

    assert compare_error_spans_lists(
        span_list1=competitor_check.compute_error_spans(
            ["Banana is a great company"], [["Apple"]]
        ),
        span_list2=[],
    )

    assert compare_error_spans_lists(
        span_list1=competitor_check.compute_error_spans(
            ["Apple is a great company", "Banana is a great company"], [["Apple"], []]
        ),
        span_list2=[ErrorSpan(start=0, end=5, reason="Competitor was found: Apple")],
    )

    assert compare_error_spans_lists(
        span_list1=competitor_check.compute_error_spans(
            ["Apple is a great Apple company", "Banana is a great company"],
            [["Apple"], []],
        ),
        span_list2=[
            ErrorSpan(start=0, end=5, reason="Competitor was found: Apple"),
            ErrorSpan(start=17, end=22, reason="Competitor was found: Apple"),
        ],
    )


def test_find_competitor_matches():
    competitor_check = CompetitorCheck(competitors=["Apple"], use_local=True)
    assert competitor_check.find_competitor_matches(["Apple is a great company"]) == [
        ["Apple"]
    ]
    assert competitor_check.find_competitor_matches(["Banana is a great company"]) == [
        []
    ]
    assert competitor_check.find_competitor_matches(
        ["Apple is a great company", "Banana is a great company"]
    ) == [["Apple"], []]
    assert competitor_check.find_competitor_matches(
        ["Apple is a great Apple company", "Banana is a great company"]
    ) == [["Apple", "Apple"], []]


def compare_error_spans(span1, span2):
    return (
        span1.start == span2.start
        and span1.end == span2.end
        and span1.reason == span2.reason
    )


def compare_error_spans_lists(span_list1, span_list2):
    if len(span_list1) != len(span_list2):
        return False
    for i in range(len(span_list1)):
        if not compare_error_spans(span_list1[i], span_list2[i]):
            return False
    return True
