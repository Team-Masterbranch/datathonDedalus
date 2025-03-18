## Fix Prompts
- !!! LLM currently creates wrong queries if we have three or more logic operands.
  Explanation: it creates "A and B and C" query, but current implementation only supports
  "((A and B) and C)" implementation: each AND/OR should have exactly 2 arguments.

  Probably, we should change implementation to decode AND with 3+ arguments.

- we have a problem with between query


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