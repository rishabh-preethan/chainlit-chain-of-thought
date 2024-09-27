import groq
import time
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

client = groq.Groq(api_key="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")

def make_api_call(messages, max_tokens, is_final_answer=False, custom_client=None):
    # client_to_use = custom_client if custom_client is not None else client
    global client

    # Log the messages being sent
    logging.debug(f"Sending messages: {messages}")

    for attempt in range(3):
        try:
            if is_final_answer:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.2,
                    # response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                logging.debug(f"Received response for final answer: {content}")
                return content
            else:
                response = client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                logging.debug(f"Received response for step: {content}")
                # Attempt to load as JSON to catch serialization issues
                return content

        except Exception as e:
            # Log the exception details
            logging.error(f"Attempt {attempt + 1}: {str(e)}")
            if attempt == 2:
                error_message = {
                    "title": "Error",
                    "content": f"Failed to generate {'final answer' if is_final_answer else 'step'} after 3 attempts. Error: {str(e)}",
                    "next_action": "final_answer" if not is_final_answer else None
                }
                logging.debug(f"Error message: {error_message}")
                return error_message
            
            time.sleep(1)  # Wait for 1 second before retrying

async def generate_response(prompt, custom_client=None):
    messages = [
        {"role": "system", "content": "You are an expert AI assistant..."},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": "Thank you! I will now think step by step..."}
    ]
    
    steps = []
    step_count = 1
    total_thinking_time = 0
    
    while True:
        start_time = time.time()
        step_data = await make_api_call(messages, 300, custom_client=custom_client)  # Await here
        end_time = time.time()
        thinking_time = end_time - start_time
        total_thinking_time += thinking_time
        
        steps.append((f"Step {step_count}: {step_data['title']}", step_data['content'], thinking_time))
        
        messages.append({"role": "assistant", "content": json.dumps(step_data)})
        
        if step_data['next_action'] == 'final_answer' or step_count > 25:
            break
        
        step_count += 1

        yield steps, total_thinking_time  # Yielding steps and total thinking time

    # Generate final answer
    messages.append({"role": "user", "content": "Please provide the final answer..."})
    
    start_time = time.time()
    final_data = await make_api_call(messages, 1200, is_final_answer=True, custom_client=custom_client)  # Await here
    end_time = time.time()
    thinking_time = end_time - start_time
    total_thinking_time += thinking_time
    
    steps.append(("Final Answer", final_data, thinking_time))

    yield steps, total_thinking_time

