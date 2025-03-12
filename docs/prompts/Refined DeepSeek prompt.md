**User’s Situation & Goals**

- **Competition**: Datathlon Challenge 2 (develop a conversational agent to identify chronic patient cohorts).
    
- **Task**: Use a pre-trained LLM (Claude 3 Sonnet via Amazon Bedrock) to build a conversational interface for healthcare professionals.
    
- **Constraints**:
    
    - No model training/fine-tuning required.
        
    - Focus on **prompt engineering**, **conversational design**, and structured outputs.
        
- **Tools Provided**:
    
    - API key for a proxy server (`litellm.dedalus.com`) to access Claude 3 Sonnet.
        
    - Example code using the OpenAI client library (configured to route requests to Bedrock).
        

**Key Requirements**:

1. Design prompts to extract precise patient cohorts (diabetes, hypertension, COPD) from data.
    
2. Create a **multi-turn dialogue flow** for refining criteria (e.g., labs, medications, exclusions).
    
3. Ensure outputs are structured (e.g., JSON/CSV) and actionable for healthcare workflows.
    

**Next Steps Discussed**:

- Use system prompts to define the agent’s role (e.g., "medical cohort assistant").
    
- Iterate on conversational logic (e.g., clarifying ambiguous criteria, validating outputs).
    
- Test edge cases (e.g., conflicting filters, missing data).