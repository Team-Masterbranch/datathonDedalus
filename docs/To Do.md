## Fix Prompts
- !!! LLM currently creates wrong queries if we have three or more logic operands.
  Explanation: it creates "A and B and C" query, but current implementation only supports
  "((A and B) and C)" implementation: each AND/OR should have exactly 2 arguments.

  Probably, we should change implementation to decode AND with 3+ arguments.