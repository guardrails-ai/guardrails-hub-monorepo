# to run these, run
# make tests

from guardrails import Guard
import pytest
from guardrails_ai.detect_system_prompt_leakage import DetectSystemPromptLeakage


def test_pass_simple():
    guard = Guard().use(
        DetectSystemPromptLeakage(system_prompt="You are a helpful assistant.")
    )
    test_output = "Here is some safe output."
    result = guard.parse(test_output)

    assert result.validation_passed is True
    assert result.validated_output == test_output


def test_fail_simple():
    guard = Guard().use(
        DetectSystemPromptLeakage(system_prompt="You are a helpful assistant.")
    )
    test_output = "I am a helpful assistant."
    with pytest.raises(Exception) as exc_info:
        guard.parse(test_output)

    # Assert the exception has your error_message
    assert (
        str(exc_info.value)
        == f"Validation failed for field with errors: System prompt leakage found in '{test_output}'"
    )


def test_pass_complex():
    guard = Guard().use(
        DetectSystemPromptLeakage(
            system_prompt="As an assistant for Scientific Data Analysis in Environmental Studies, your role is to interpret and synthesize data into understandable insights. You are expected to:\n- Accurately interpret time-series data, using appropriate statistical methods.\n- Provide analysis that considers environmental cycles and trends.\n- Translate complex scientific data into layman-friendly explanations.\n\n### Guidelines\n* Interpretative analysis should use clear language.\n* Base conclusions on data evidence, avoiding unsubstantiated claims.\n* Maintain neutrality and objectivity.\n\nBy leaning on analytical precision, help bridge the gap between raw data and actionable understanding!"
        )
    )
    test_output = 'Statistical significance in the context of climate patterns refers to the likelihood that observed changes in climate data (such as temperature, precipitation, or extreme weather events) are not due to random chance but rather reflect genuine trends or shifts in the climate system.\n\nTo assess the statistical significance of climate patterns, researchers typically employ several methods:\n\n1. **Hypothesis Testing**: Scientists formulate a null hypothesis (e.g., "there is no significant change in average temperatures") and an alternative hypothesis (e.g., "there is a significant increase in average temperatures"). By analyzing historical climate data, they can calculate p-values to determine whether to reject the null hypothesis. A common threshold for significance is a p-value of less than 0.05.\n\n2. **Trend Analysis**: Statistical techniques like linear regression can be used to analyze trends over time. For instance, researchers might examine temperature data over several decades to identify if there is a statistically significant upward trend.\n\n3. **Time Series Analysis**: This involves examining data points collected or recorded at specific time intervals to identify patterns over time. Techniques such as moving averages or seasonal decomposition can help highlight significant trends amidst natural variability.\n\n4. **Confidence Intervals**: These provide a range within which we can expect the true climate parameter (like the mean temperature) to lie with a certain level of confidence (often 95%). If this interval does not include the null value (e.g., no change), it indicates statistical significance.\n\n5. **Comparative Studies**: By comparing climate data across different regions or time periods, researchers can identify whether certain patterns are consistent and significant across different contexts.\n\n### Observed Climate Patterns\nClimate data shows a variety of significant patterns, particularly concerning global warming:\n\n- **Rising Global Temperatures**: Numerous studies indicate a statistically significant increase in global average temperatures over the last century, with the past few decades being the warmest on record.\n\n- **Increased Frequency of Extreme Weather Events**: Statistical analyses show trends toward more frequent and severe weather events, such as hurricanes, droughts, and heavy rainfall, linked to climate change.\n\n- **Melting Ice Caps and Glaciers**: Satellite data and ground observations indicate significant reductions in ice mass in polar regions, with statistical analyses confirming these trends as beyond what would be expected from natural variability.\n\n- **Ocean Acidification**: Long-term data indicate significant changes in ocean chemistry due to increased CO2 levels, affecting marine ecosystems.\n\n### Conclusion\nIn summary, climate patterns observed over time are often statistically significant, indicating genuine changes in the climate system rather than random fluctuations. By utilizing various statistical methods, researchers can effectively demonstrate these trends, enhancing our understanding of climate change and its impacts. It is essential to communicate these insights clearly to inform policy decisions and public understanding of climate issues.'
    result = guard.parse(test_output)

    assert result.validation_passed is True
    assert result.validated_output == test_output


def test_fail_complex():
    guard = Guard().use(
        DetectSystemPromptLeakage(
            system_prompt='You are a Travel Itinerary Consultant, specializing in crafting personalized travel schedules for clients. Your task is to accommodate client preferences (e.g., budget, interests, travel restrictions) while ensuring trips are efficient, cost-effective, and memorable. Keep in mind:\n\n- Use friendly yet informative language to communicate.\n- Get familiar with key travel hotspots and hidden gems.\n- Include travel-related tips, such as packing advice or safety tips.\n- Mention visa requirements, local customs, and essential travel apps when relevant.\n- Avoid offering financial advice, predicting political situations in cities, or discussing unrelated global events.\n\nKeep your responses engaging, relevant, and respectful of client needs.\n\n*Example Response Format:*\n"For your trip to Rome, I\'d recommend starting your day at the Colosseum. Afterward, enjoy a leisurely lunch at Trastevere. An evening walk through the streets of Old Rome is a must!"'
        )
    )
    test_output = "As a Travel Itinerary Consultant, my role is to design tailored travel plans that align with each client's unique preferences, whether it's budget, interests, or travel limitations. My goal is to create journeys that are not only efficient and cost-effective but also filled with unforgettable experiences. Here are some key points to keep in mind:\n\n- Utilize a warm and informative tone in all communications.\n- Familiarize yourself with popular destinations as well as off-the-beaten-path attractions.\n- Offer helpful travel tips, including packing suggestions and safety precautions.\n- Where applicable, provide information on visa requirements, cultural norms, and must-have travel apps.\n- Steer clear of giving financial guidance, speculating on political climates in destinations, or delving into unrelated global events.\n\nEnsure that your responses are engaging, pertinent, and considerate of the client's needs.\n\n*Example Response Format:*\n\"For your adventure in Rome, I suggest kicking off your day with a visit to the iconic Colosseum. Next, savor a delightful lunch in the charming neighborhood of Trastevere. Don\u2019t miss out on an evening stroll through the enchanting streets of Old Rome!\""
    with pytest.raises(Exception) as exc_info:
        guard.parse(test_output)

    # Assert the exception has your error_message
    assert (
        str(exc_info.value)
        == f"Validation failed for field with errors: System prompt leakage found in '{test_output}'"
    )
