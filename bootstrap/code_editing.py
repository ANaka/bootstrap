
from langchain import LLMChain
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from functools import partial

code_editor_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
I will give you a function/class definition and some instructions on how to edit it. You will rewrite the code according to the instrucitons.

{input}

Edit the code and provide it in the following format:

```python
<edited code>
```

Provide only the edited code. Do not provide any imports or other code that is not part of the function/class definition you are editing.
""",
)

EditorChain = partial(
    LLMChain,
    llm=OpenAI(model_name="gpt-4", temperature=0.3),
    prompt=code_editor_prompt,
    output_key="edited_code",
)