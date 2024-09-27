import chainlit as cl
from g1 import generate_response
import json
import groq

client = groq.Groq(api_key="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")

@cl.on_message
async def main(message: str):
    await cl.Message(content="Generating response...").send()

    steps = []
    total_thinking_time = 0  # Initialize total_thinking_time here

    async for step_data, thinking_time in generate_response(message.content):  # Use async for
        steps.extend(step_data)
        total_thinking_time += thinking_time  # Accumulate total_thinking_time

        for i, (title, content, thinking_time) in enumerate(step_data):
            if title.startswith("Final Answer"):
                if '```' in content:
                    parts = content.split('```')
                    for index, part in enumerate(parts):
                        if index % 2 == 0:
                            await cl.Message(content=part).send()
                        else:
                            if '\n' in part:
                                lang_line, code = part.split('\n', 1)
                                lang = lang_line.strip()
                            else:
                                lang = ''
                                code = part
                            await cl.Message(content=f"```{lang}\n{code}\n```").send()  # Removed mime_type
                else:
                    escaped_content = json.dumps(content) if not isinstance(content, str) else content
                    await cl.Message(content=escaped_content).send()  # Removed mime_type
            else:
                escaped_content = json.dumps(content) if not isinstance(content, str) else content
                escaped_content = escaped_content.replace('\n', '<br>')  # Replace newlines with <br>
                await cl.Message(content=f"**{title}**<br>{escaped_content}").send()  # Removed mime_type

    if total_thinking_time is not None:
        await cl.Message(content=f"**Total thinking time: {total_thinking_time:.2f} seconds**").send()  # Removed mime_type
