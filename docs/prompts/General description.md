I am participating in a Datathlon (IT/Data Science competition for students).
The task I am working on is this:

"Challenge 2: Creation of a Conversational Agent to Identify Cohorts of Chronic Patients
The goal of this challenge is to develop a conversational agent that enables healthcare professionals to quickly and efficiently identify cohorts of patients with chronic diseases (diabetes, hypertension, COPD, etc.)."

The organizers promised to provide access to some model on Amazon Bedrock, but I am unsure about the details as I have no experience with it.

Here is the message from a mentor:

"Aquí está vuestra secret key para consumir la api que deberéis usar en el código de abajo.

ACTUAL KEY REDACTED

Aqui abajo tenéis código ejemplo

import openai # openai v1.0.0+  
client = openai.OpenAI(api_key="VirtualAPIKey",base_url="https://litellm.dccp.pbu.dedalus.com") # set proxy to base_url  
# request sent to model set on litellm proxy, `litellm --model`  
response = client.chat.completions.create(model="bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0", messages = [  
    {  
        "role": "user",  
        "content": "this is a test request, write a short poem"  
    }  
])"