LLM Instructions
========================

Sitocm Simulator uses large language models (LLMs) in several places.
The default prompts are shown below.
They are overridable.
They are subject to change frequently as improvements are discovered.

Script Writing
--------------

Parameters: ``characters``, ``music_categories``, ``prompt``

.. literalinclude:: ..//sitcom_simulator/script/llm_instructions.txt
   :language: text
   :caption: llm_instructions.txt

Character Extraction
--------------------

Parameters: ``prompt``

.. literalinclude:: ..//sitcom_simulator/script/integrations/fakeyou/character_extraction_instructions.txt
   :language: text
   :caption: llm_instructions.txt