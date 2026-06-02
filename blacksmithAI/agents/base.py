from langchain_openai import ChatOpenAI
import json
from dotenv import load_dotenv
import os
from langchain.tools import tool
import requests
from langgraph.config import get_stream_writer
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from rich import print
from rich.console import Console
from deepagents import create_deep_agent, CompiledSubAgent

load_dotenv()

config = json.load(open("config.json", "r"))
console = Console()

# 根据环境变量或配置文件选择 provider
default_provider = os.getenv('BLACKSMITH_PROVIDER', config['defaults']['provider'])
base_url = config['provider'][default_provider]['base_url']
api_key_env = f"{default_provider.upper()}_API_KEY"
api_key = os.getenv(api_key_env, "")

# 获取模型配置
default_model = config['provider'][default_provider]['default_model']
context_size = config['provider'][default_provider]['default_model_config']['context_size']
max_retries = config['provider'][default_provider]['default_model_config']['max_retries']
stream_usage = config['provider'][default_provider]['default_model_config']['stream_usage']
max_tokens = config['provider'][default_provider]['default_model_config']['max_tokens']

print(f"[bold green]✓ 使用 Provider: {default_provider}[/bold green]")
print(f"[bold green]✓ 模型: {default_model}[/bold green]")
print(f"[bold green]✓ API 端点: {base_url}[/bold green]")

# 初始化模型（添加 extra_body 关闭思考模式）
model = ChatOpenAI(
    name='pentester_nmap',
    model=default_model,
    api_key=api_key,
    base_url=base_url,
    stream_usage=stream_usage,
    max_retries=max_retries,
    max_completion_tokens=max_tokens,
    extra_body={"thinking": {"type": "disabled"}} if default_provider == "deepseek" else None,
)

#define nmap tool

@tool
def pentest_shell(command: str):
    """
    This tool run a shell commands for pentesting.
    You can install new tools that would help you pentest.
    As of now these tools are available [nmap nikto curl hping3 whois dig nslookup dnsrecon dirb sqlmap hydra john gobuster wpscan hydra] besides basic linux commands.
    
    Args:
        command: bash command e.g nmap -sV -p 80,21 10.10.1.173
    """

    writer = get_stream_writer()
    writer(f"running command {command}")

    response = requests.post(
        os.getenv('container_uri', 'http://localhost:9756/exec'),
        json={"cmd": command}
    )
    return response.json()

pentester_agent = create_agent(
    model=model,
    tools=[pentest_shell],
    system_prompt="you are a penetration tester. testing systems and devices using the tools provided.",
    checkpointer=InMemorySaver(),
    name='pentester_agent',
    middleware= [
        SummarizationMiddleware(
          model=model,
          trigger=("fraction", 0.8), 
        )
    ]
)


dp = create_deep_agent(
    base_agent=pentester_agent,
    name="pentester_deep_agent",
    sub_agents=[
        CompiledSubAgent(
            name="recon_agent",
            description="""
                You are a pentester and control a Linux sandbox. You may install packages, run system commands, and perform tests. 
                You are encourged to run and analyze complex commands that would help in executing users task.
                The user might request long running tasks that may require complex execution, timing and analysis. 
                your task is help the user in the best possible way for penetration testing tasks.""",
            runnable=pentester_agent,
        )
    ],
)


config = {'configurable': {'thread_id': 'convo_1'}}

import time

print("----- wellcome to agent portal -------")
print("loading...............................")

while True:

    time.sleep(2)

    try:
        user_input = str(console.input("\n[bold green]message to agent > [/bold green]"))
    except KeyboardInterrupt:
        print("\n[bold red]exiting...[/bold red]")
        time.sleep(3)
        break

    if user_input == 'exit':
        break

    for mode, chunk in pentester_agent.stream({'messages': [HumanMessage(user_input)]}, config=config, stream_mode=['values', 'custom']):

        if mode == 'values':
            chunk['messages'][-1].pretty_print()
        if mode == 'custom':
            print(f"[bold blue]{chunk}[/bold blue]", end='', flush=True)
root@ubuntu2024:/home/qwe/blacksmith/blacksmithAI# cat agents/base.py
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import json
from openai import RateLimitError

load_dotenv()

#load configuration
config = json.load(open("./config.json", "r"))

# select provider and model
default_provider = config['defaults']['provider']

base_url = config['provider'][f'{default_provider}']['base_url'] or 'https://openrouter.ai/api/v1' # default openrouter
default_model = config['provider'][f'{default_provider}']['default_model'] or "mistralai/devstral-2512"
context_size = config['provider'][f'{default_provider}']['default_model_config']['context_size'] or 200000
max_retries = config['provider'][f'{default_provider}']['default_model_config']['max_retries'] or 3
stream_usage = config['provider'][f'{default_provider}']['default_model_config']['stream_usage'] or True
max_tokens = config['provider'][f'{default_provider}']['default_model_config']['max_tokens'] or None
embedding_model = config['provider'][f'{default_provider}']['default_embedding_model'] or "openai/text-embedding-3-small"

# api key
key = f'{default_provider.upper()}_API_KEY'
api_key = os.getenv(key, "") # get key from env


class init_model:
    def __init__(self, reasoning_effort=None, temperature=0):
        # Disable internal retries to avoid conflicts, use with_retry instead
        self.model = ChatOpenAI(
            model=default_model,
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
            stream_usage=stream_usage,
            profile={"max_input_tokens": context_size},
            reasoning_effort=reasoning_effort,
            temperature=temperature,
            max_completion_tokens=max_tokens
        , extra_body={"thinking": {"type": "disabled"}})

    def get_model(self):
        return self.model
    
class init_embedding_model():
    
    def __init__(self):

        self.model = OpenAIEmbeddings(
            model=embedding_model,
            api_key=api_key,
            base_url=base_url,
            max_retries=max_retries,
        )

    def get_model(self):
        return self.model
    
