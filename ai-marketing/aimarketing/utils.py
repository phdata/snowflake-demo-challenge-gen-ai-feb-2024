import os
import datetime
import json
import requests
import re

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def request_post_retry(url, headers, payload):
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response


MAX_TOKENS = 300


def submit_prompt(
    system_prompt: str, user_prompt: str, use_streamlit: bool = True, log: bool = True
) -> str:
    url = os.getenv("LLM_URL", "http://localhost:8001/v1/chat/completions")
    if url.split("/")[-1] == "generate":
        megatron = True
    else:
        megatron = False

    input_prompt = f"{system_prompt}\n\n{user_prompt}"

    if megatron:
        payload = {
            "sentences": [input_prompt],
            "tokens_to_generate": MAX_TOKENS,
            "temperature": 0.15,
            "add_BOS": True,
            "top_k": 0,
            "top_p": 0.9,
            "greedy": False,
            "all_probs": False,
            "repetition_penalty": 1.2,
            "min_tokens_to_generate": 2,
        }
    else:
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": MAX_TOKENS,
            "stream": True,
        }


    headers = {
        "Content-Type": "application/json",
    }

    if megatron:
        response = requests.put(url, data=json.dumps(payload), headers=headers)
        print(response)
        with open("app/log.md", "a") as f:
            f.write(f"# {response}\n")
    else:
        response = request_post_retry(url, headers, payload)

    if use_streamlit:
        import streamlit as st

        response_container = st.empty()
        if megatron:
            formatted_reply = response.json()['sentences'][0].replace(input_prompt, "", 1)
            response_container.markdown(formatted_reply)
        else:
            collected_messages = []
            for chunk in parse_stream(response.iter_lines()):
                chunk_message = chunk["choices"][0]["delta"]
                collected_messages.append(chunk_message)
                full_reply_content = "".join(
                    [m.get("content", "") for m in collected_messages]
                )
                formatted_reply = re.sub(
                    r"\n+", "\n\n", full_reply_content, flags=re.MULTILINE
                )
                response_container.markdown(formatted_reply)
    else:
        if megatron:
            formatted_reply = response.json()['sentences'][0].replace(input_prompt, "", 1)
        else:
            full_reply_content = response.json()["choices"][0]["message"]["content"]
            formatted_reply = re.sub(r"\n+", "\n\n", full_reply_content, flags=re.MULTILINE)

    if log:
        with open("app/log.md", "a") as f:
            f.write(f"# {datetime.datetime.now()}\n")
            prompt_markdown = "  \n".join(system_prompt.split("\n"))
            f.write(f"## System Prompt\n{prompt_markdown}\n")
            prompt_markdown = "  \n".join(user_prompt.split("\n"))
            f.write(f"## User Prompt\n{prompt_markdown}\n")
            f.write(f"## Reply\n{formatted_reply}\n")

    return formatted_reply


def parse_stream(rbody):
    prefix = b"data: "
    len_prefix = len(prefix)
    for line in rbody:
        if line:
            if line.strip() == b"data: [DONE]":
                return
            elif line.startswith(prefix):
                line = line[len_prefix:]
                yield json.loads(line.decode("utf-8"))


if __name__ == "__main__":
    current_date = datetime.date.today()

    for i in range(0, 45, 3):
        date = current_date - datetime.timedelta(days=i)
        print(date, "=>", humanize_with_gpt(date, current_date))

    for i in range(45, 600, 30):
        date = current_date - datetime.timedelta(days=i)
        print(date, "=>", humanize_with_gpt(date, current_date))
