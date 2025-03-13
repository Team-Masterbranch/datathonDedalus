#### Quick features
- add Spanish version of commands.
#### Add modules:
**Pre-parser:** This module will parse basic inputs before actually calling LLM. We just use GREP to try to understand basic cases. Like, if someone type "Dame la liste de pacientes con [$condition_name]" this parser should convert it into query and not use LLM. This will improve computational efficiency.

**Cache of user input:** we should store user inputs and LLM responses there. If someone would repeat same input, we do not call LLM, and just repeat the response. Again, for improving efficiency.