<!-- Generated from validator manifests; each package name links to its PyPI project. -->
# Guardrails Validators

Validators published to public PyPI as `guardrails-ai-<name>`, grouped by risk category. Install with `pip install <package>`; each package name links to its PyPI page.

## Brand risk

- **Ban List** ([`guardrails-ai-ban-list`](https://pypi.org/project/guardrails-ai-ban-list/)): Validates that the output does not contain banned words, using fuzzy search.
- **Bert Toxic Language Validator** ([`guardrails-ai-bert-toxic`](https://pypi.org/project/guardrails-ai-bert-toxic/)): Validates that the input string does not contain toxic language based on a BERT model.
- **Bias Check** ([`guardrails-ai-bias-check`](https://pypi.org/project/guardrails-ai-bias-check/)): Validates that the text is free from biases related to age, gender, sex, ethnicity, religion, etc.
- **Competitor Check** ([`guardrails-ai-competitor-check`](https://pypi.org/project/guardrails-ai-competitor-check/)): Flags mentions of competitors. Fixes responses by filtering out competitor names.
- **Cucumber Expression Match** ([`guardrails-ai-cucumber-expression-match`](https://pypi.org/project/guardrails-ai-cucumber-expression-match/)): Validates that the input string matches a specified cucumber expression.
- **Detect Jailbreak** ([`guardrails-ai-detect-jailbreak`](https://pypi.org/project/guardrails-ai-detect-jailbreak/)): Detects attempts to circumvent safeguards in model conditioning.
- **Extracted Summary Sentences Match** ([`guardrails-ai-extracted-summary-sentences-match`](https://pypi.org/project/guardrails-ai-extracted-summary-sentences-match/)): This validator checks if the extracted summary sentences match the original document.
- **Gibberish Text** ([`guardrails-ai-gibberish-text`](https://pypi.org/project/guardrails-ai-gibberish-text/)): A Guardrails AI validator to detect gibberish text.
- **Logic Check** ([`guardrails-ai-logic-check`](https://pypi.org/project/guardrails-ai-logic-check/)): Validates logical consistency and detects logical fallacies in the model output. Attempts to correct logical fallacies if found.
- **Profanity Free** ([`guardrails-ai-profanity-free`](https://pypi.org/project/guardrails-ai-profanity-free/)): Checks for profanity in text, using the alt-profanity-check library.
- **Provenance Embeddings** ([`guardrails-ai-provenance-embeddings`](https://pypi.org/project/guardrails-ai-provenance-embeddings/)): Compares embeddings of generated and source texts to calculate provenance.
- **Provenance LLM** ([`guardrails-ai-provenance-llm`](https://pypi.org/project/guardrails-ai-provenance-llm/)): A validator for ensuring the factuality and reducing brand risk in generated content.
- **QA Relevance LLM Eval** ([`guardrails-ai-qa-relevance-llm-eval`](https://pypi.org/project/guardrails-ai-qa-relevance-llm-eval/)): Makes a second request to the LLM, asking it if its original response was relevant to the prompt.
- **Quotes Price** ([`guardrails-ai-quotes-price`](https://pypi.org/project/guardrails-ai-quotes-price/)): Validates that the generated text contains a price quote
- **Reading Level** ([`guardrails-ai-reading-level`](https://pypi.org/project/guardrails-ai-reading-level/)): Parses text to find its readability as a US grade level number (0-12).
- **Relevancy Evaluator** ([`guardrails-ai-relevancy-evaluator`](https://pypi.org/project/guardrails-ai-relevancy-evaluator/)): Validates that the reference text contains information relevant to answering the original question.
- **Sky Validator** ([`guardrails-ai-sky-validator`](https://pypi.org/project/guardrails-ai-sky-validator/)): Validates that the input string does not contain negative statements about Sky Electric.

## Code Exploits

- **Endpoint Is Reachable** ([`guardrails-ai-endpoint-is-reachable`](https://pypi.org/project/guardrails-ai-endpoint-is-reachable/)): Checks if an endpoint can be reached by making a request to it.
- **Exclude SQL Predicates** ([`guardrails-ai-exclude-sql-predicates`](https://pypi.org/project/guardrails-ai-exclude-sql-predicates/)): This rule checks for the use of particular SQL predicates in the query. It is important to exclude SQL predicates from the query to prevent SQL injection attacks.
- **Has Url** ([`guardrails-ai-has-url`](https://pypi.org/project/guardrails-ai-has-url/)): Ensure content contains a url.
- **Web Sanitization** ([`guardrails-ai-web-sanitization`](https://pypi.org/project/guardrails-ai-web-sanitization/)): Scans LLM outputs for strings that could cause browser script execution downstream.

## Data Leakage

- **African PII** (`guardrails-ai-african-pii`](https://pypi.org/project/guardrails-ai-african-pii/)): Detects African-specific PII — BVN, NIN, Ghana Card, KRA PIN, SA ID, and phone formats across NG, KE, ZA, GH, RW, EG.
- **Detect PII** ([`guardrails-ai-detect-pii`](https://pypi.org/project/guardrails-ai-detect-pii/)): Detects personally identifiable information (PII) in text, using Microsoft Presidio.
- **Detect System Prompt Leakage** ([`guardrails-ai-detect-system-prompt-leakage`](https://pypi.org/project/guardrails-ai-detect-system-prompt-leakage/)): Detects system prompt leakage using fuzzy string matching (via `rapidfuzz`) to compare the LLM's response against a provided system prompt
- **Exclude SQL Predicates** ([`guardrails-ai-exclude-sql-predicates`](https://pypi.org/project/guardrails-ai-exclude-sql-predicates/)): This rule checks for the use of particular SQL predicates in the query. It is important to exclude SQL predicates from the query to prevent SQL injection attacks.
- **Guardrails PII** ([`guardrails-ai-guardrails-pii`](https://pypi.org/project/guardrails-ai-guardrails-pii/)): Detects personally identifiable information (PII) in text.
- **Internal Domains** ([`guardrails-ai-internal-domains`](https://pypi.org/project/guardrails-ai-internal-domains/)): Identifies internal domains in a string output.
- **Presidio Gliner PII** ([`guardrails-ai-presidio-gliner-pii`](https://pypi.org/project/guardrails-ai-presidio-gliner-pii/)): Detects personally identifiable information (PII) in text.
- **Secrets Present** ([`guardrails-ai-secrets-present`](https://pypi.org/project/guardrails-ai-secrets-present/)): Detects the secrets present in text by matching against common patterns for API keys and other sensitive information.

## Etiquette

- **Detect Jailbreak** ([`guardrails-ai-detect-jailbreak`](https://pypi.org/project/guardrails-ai-detect-jailbreak/)): Detects attempts to circumvent safeguards in model conditioning.
- **LLM Critic** ([`guardrails-ai-llm-critic`](https://pypi.org/project/guardrails-ai-llm-critic/)): Grade the generated response based on provided criteria.
- **Llama Guard** ([`guardrails-ai-llamaguard-7b`](https://pypi.org/project/guardrails-ai-llamaguard-7b/)): A llama based validator which checks whether a given prompt is safe/unsafe by specifying a set of  policies and lists the violating policies when applicable.
- **Mentions Drugs** ([`guardrails-ai-mentions-drugs`](https://pypi.org/project/guardrails-ai-mentions-drugs/)): Validates that the generated text does not contain any drug names
- **NSFW Text** ([`guardrails-ai-nsfw-text`](https://pypi.org/project/guardrails-ai-nsfw-text/)): A Guardrails AI validator to detect NSFW text
- **Politeness Check** ([`guardrails-ai-politeness-check`](https://pypi.org/project/guardrails-ai-politeness-check/)): Ensure generated output is polite.
- **Profanity Free** ([`guardrails-ai-profanity-free`](https://pypi.org/project/guardrails-ai-profanity-free/)): Checks for profanity in text, using the alt-profanity-check library.
- **Reading Level** ([`guardrails-ai-reading-level`](https://pypi.org/project/guardrails-ai-reading-level/)): Parses text to find its readability as a US grade level number (0-12).
- **Redundant Sentences** ([`guardrails-ai-redundant-sentences`](https://pypi.org/project/guardrails-ai-redundant-sentences/)): Identifies redundant sentences in text using fuzzy matching.
- **Response Evaluator** ([`guardrails-ai-response-evaluator`](https://pypi.org/project/guardrails-ai-response-evaluator/)): Evaluate generated output using a provided question.
- **Restrict To Topic** ([`guardrails-ai-restrict-to-topic`](https://pypi.org/project/guardrails-ai-restrict-to-topic/)): Checks that a text stays on a set of valid topics and avoids invalid ones.
- **Sensitive Topic** ([`guardrails-ai-sensitive-topics`](https://pypi.org/project/guardrails-ai-sensitive-topics/)): A Guardrails AI validator that detects sensitive topics in text.
- **Shield Gemma** ([`guardrails-ai-shieldgemma-2b`](https://pypi.org/project/guardrails-ai-shieldgemma-2b/)): A Gemma based validator for moderating user prompts to guard against harmful content by specifying a policy.
- **Toxic Language** ([`guardrails-ai-toxic-language`](https://pypi.org/project/guardrails-ai-toxic-language/)): Identifies and flags toxic language in text to ensure communications remain professional and appropriate.
- **Toxic Language LLM** ([`guardrails-ai-toxic-language-llm`](https://pypi.org/project/guardrails-ai-toxic-language-llm/)): Detects toxic language in LLM-generated text using an LLM as the detection backbone. Evaluates text across seven toxicity categories: toxicity, severe toxicity, obscene, threat, insult, identity attack, and sexual explicit content.
- **Unusual Prompt** ([`guardrails-ai-unusual-prompt`](https://pypi.org/project/guardrails-ai-unusual-prompt/)): A Guardrails AI input validator that validates a prompt for unusualness and trickery.

## Factuality

- **Extracted Summary Sentences Match** ([`guardrails-ai-extracted-summary-sentences-match`](https://pypi.org/project/guardrails-ai-extracted-summary-sentences-match/)): This validator checks if the extracted summary sentences match the original document.
- **Gibberish Text** ([`guardrails-ai-gibberish-text`](https://pypi.org/project/guardrails-ai-gibberish-text/)): A Guardrails AI validator to detect gibberish text.
- **LLM Critic** ([`guardrails-ai-llm-critic`](https://pypi.org/project/guardrails-ai-llm-critic/)): Grade the generated response based on provided criteria.
- **Provenance Embeddings** ([`guardrails-ai-provenance-embeddings`](https://pypi.org/project/guardrails-ai-provenance-embeddings/)): Compares embeddings of generated and source texts to calculate provenance.
- **Provenance LLM** ([`guardrails-ai-provenance-llm`](https://pypi.org/project/guardrails-ai-provenance-llm/)): A validator for ensuring the factuality and reducing brand risk in generated content.
- **Provenance NLI** ([`guardrails-ai-provenance-nli`](https://pypi.org/project/guardrails-ai-provenance-nli/)): Detects and removes hallucinations from LLM-generated text using an NLI model to validate it against a provided context.
- **Response Evaluator** ([`guardrails-ai-response-evaluator`](https://pypi.org/project/guardrails-ai-response-evaluator/)): Evaluate generated output using a provided question.
- **Responsiveness Check** ([`guardrails-ai-responsiveness-check`](https://pypi.org/project/guardrails-ai-responsiveness-check/)): Ensure generated output is polite.
- **Saliency Check** ([`guardrails-ai-saliency-check`](https://pypi.org/project/guardrails-ai-saliency-check/)): Checks if a generated summary covers topics present in a source document.
- **Similar To Document** ([`guardrails-ai-similar-to-document`](https://pypi.org/project/guardrails-ai-similar-to-document/)): Checks if some generated text is similar to a provided document.
- **Similar To Previous Values** ([`guardrails-ai-similar-to-previous-values`](https://pypi.org/project/guardrails-ai-similar-to-previous-values/)): Checks if a value is similar to a list of previously known correct values.
- **Valid Address** ([`guardrails-ai-valid-address`](https://pypi.org/project/guardrails-ai-valid-address/)): Verifies an LLM-generated address using Google Maps' Address Validation API.
- **Wiki Provenance** ([`guardrails-ai-wiki-provenance`](https://pypi.org/project/guardrails-ai-wiki-provenance/)): A Guardrails AI validator that detects and removes hallucinated text based off Wikipedia

## Formatting

- **Contains String** ([`guardrails-ai-contains-string`](https://pypi.org/project/guardrails-ai-contains-string/)): A Guardrails AI validator to check if the LLM-generated text contains a substring.
- **Ends With** ([`guardrails-ai-ends-with`](https://pypi.org/project/guardrails-ai-ends-with/)): Check if a string or list ends with a specified string or list.
- **Gibberish Text** ([`guardrails-ai-gibberish-text`](https://pypi.org/project/guardrails-ai-gibberish-text/)): A Guardrails AI validator to detect gibberish text.
- **Lowercase** ([`guardrails-ai-lowercase`](https://pypi.org/project/guardrails-ai-lowercase/)): Passes when totally lowercase.
- **One Line** ([`guardrails-ai-one-line`](https://pypi.org/project/guardrails-ai-one-line/)): This validator checks if the input is a single line of text.
- **Reading Time** ([`guardrails-ai-reading-time`](https://pypi.org/project/guardrails-ai-reading-time/)): Ensures that any generated text is less than a maximum expected reading time.
- **Regex Match** ([`guardrails-ai-regex-match`](https://pypi.org/project/guardrails-ai-regex-match/)): Ensure content matches a provided regular expression. This can be used to validate content such as email addresses, phone numbers, and more.
- **Two Words** ([`guardrails-ai-two-words`](https://pypi.org/project/guardrails-ai-two-words/)): Passes when value is *exactly* two words.
- **Uppercase** ([`guardrails-ai-uppercase`](https://pypi.org/project/guardrails-ai-uppercase/)): Passes when totally uppercase.
- **Valid Address** ([`guardrails-ai-valid-address`](https://pypi.org/project/guardrails-ai-valid-address/)): Verifies an LLM-generated address using Google Maps' Address Validation API.
- **Valid Choices** ([`guardrails-ai-valid-choices`](https://pypi.org/project/guardrails-ai-valid-choices/)): Checks if a given string is a valid choice from a list of choices.
- **Valid HTML** ([`guardrails-ai-valid-html`](https://pypi.org/project/guardrails-ai-valid-html/)): Guardrails validator that checks for HTML parseability.
- **Valid JSON** ([`guardrails-ai-valid-json`](https://pypi.org/project/guardrails-ai-valid-json/)): Ensure content is parseable as valid JSON.
- **Valid Length** ([`guardrails-ai-valid-length`](https://pypi.org/project/guardrails-ai-valid-length/)): Ensures the length of a string or list falls between a minimum and maximum.
- **Valid OpenAPI Specification** ([`guardrails-ai-valid-open-api-spec`](https://pypi.org/project/guardrails-ai-valid-open-api-spec/)): Ensures that a generated output is a valid OpenAPI Specification.
- **Valid Range** ([`guardrails-ai-valid-range`](https://pypi.org/project/guardrails-ai-valid-range/)): Assess whether a generated number is between a maximum and minimum value.
- **Valid SQL** ([`guardrails-ai-valid-sql`](https://pypi.org/project/guardrails-ai-valid-sql/)): Validates whether the given SQL code is syntactically correct using. Optionally accepts a database schema to validate against using SQLAlchemy.
- **Valid URL** ([`guardrails-ai-valid-url`](https://pypi.org/project/guardrails-ai-valid-url/)): Validates that text is a syntactically-valid URL

## Invalid Code

- **Endpoint Is Reachable** ([`guardrails-ai-endpoint-is-reachable`](https://pypi.org/project/guardrails-ai-endpoint-is-reachable/)): Checks if an endpoint can be reached by making a request to it.
- **Exclude SQL Predicates** ([`guardrails-ai-exclude-sql-predicates`](https://pypi.org/project/guardrails-ai-exclude-sql-predicates/)): This rule checks for the use of particular SQL predicates in the query. It is important to exclude SQL predicates from the query to prevent SQL injection attacks.
- **Gibberish Text** ([`guardrails-ai-gibberish-text`](https://pypi.org/project/guardrails-ai-gibberish-text/)): A Guardrails AI validator to detect gibberish text.
- **Valid JSON** ([`guardrails-ai-valid-json`](https://pypi.org/project/guardrails-ai-valid-json/)): Ensure content is parseable as valid JSON.
- **Valid OpenAPI Specification** ([`guardrails-ai-valid-open-api-spec`](https://pypi.org/project/guardrails-ai-valid-open-api-spec/)): Ensures that a generated output is a valid OpenAPI Specification.
- **Valid SQL** ([`guardrails-ai-valid-sql`](https://pypi.org/project/guardrails-ai-valid-sql/)): Validates whether the given SQL code is syntactically correct using. Optionally accepts a database schema to validate against using SQLAlchemy.

## Jailbreaking

- **Detect Jailbreak** ([`guardrails-ai-detect-jailbreak`](https://pypi.org/project/guardrails-ai-detect-jailbreak/)): Detects attempts to circumvent safeguards in model conditioning.
- **Detect Prompt Injection** ([`guardrails-ai-detect-prompt-injection`](https://pypi.org/project/guardrails-ai-detect-prompt-injection/)): Finds prompt injection using the Rebuff prompt library.
- **Has Url** ([`guardrails-ai-has-url`](https://pypi.org/project/guardrails-ai-has-url/)): Ensure content contains a url.
- **Prompt Injection Detector** ([`guardrails-ai-prompt-injection-detector`](https://pypi.org/project/guardrails-ai-prompt-injection-detector/)): A Guardrails validator that scores prompts for injection attempts via a secondary LLM.
- **QA Relevance LLM Eval** ([`guardrails-ai-qa-relevance-llm-eval`](https://pypi.org/project/guardrails-ai-qa-relevance-llm-eval/)): Makes a second request to the LLM, asking it if its original response was relevant to the prompt.
- **Response Evaluator** ([`guardrails-ai-response-evaluator`](https://pypi.org/project/guardrails-ai-response-evaluator/)): Evaluate generated output using a provided question.
- **Unusual Prompt** ([`guardrails-ai-unusual-prompt`](https://pypi.org/project/guardrails-ai-unusual-prompt/)): A Guardrails AI input validator that validates a prompt for unusualness and trickery.
