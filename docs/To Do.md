## Branch description

LLM interacrion flow now:
  1) we parse user intencion from input (this could be filter or anything else, like 
     help request or visualization request).
  2) we call LLM second time to make analysis of a new dataset.

I want to change LLM interaction flow in this way:
  1) we parse user input only to decide: is it a filter query request or no.
     If it is a filter request, we do filtering. If not, we do nothing at this step.
  2) now we analuze request (so, HELP request would be analyzed on this step, and 
     not in step 1, like it was before).
     Only on this step we will decide what to do: form visualization requests,
     provide text statistics, etc.


## Fix Prompts
- !!! LLM currently creates wrong queries if we have three or more logic operands.
  Explanation: it creates "A and B and C" query, but current implementation only supports
  "((A and B) and C)" implementation: each AND/OR should have exactly 2 arguments.

  Probably, we should change implementation to decode AND with 3+ arguments.


## Query problems
- un request "dame mujeres menor que 30 y hombres mayor que 60"
  produce esa query:
      "query": {
        "operation": "or",
        "criteria": [
            {
                "operation": "and",
                "criteria": [
                    {
                        "field": "pacientes.Genero",
                        "operation": "equals",
                        "value": "Femenino"
                    },
                    {
                        "field": "pacientes.Edad",
                        "operation": "less_than",
                        "value": 30
                    }
                ]
            },
            {
                "operation": "and",
                "criteria": [
                    {
                        "field": "pacientes.Genero",
                        "operation": "equals",
                        "value": "Masculino"
                    },
                    {
                        "field": "pacientes.Edad",
                        "operation": "greater_than",
                        "value": 60
                    }
                ]
            }
        ]
    }

    que parece bien pero no ejecuta.