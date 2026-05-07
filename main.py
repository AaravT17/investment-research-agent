# ruff: noqa: E402
from dotenv import load_dotenv

load_dotenv()

from agent import agent
from models import InvestmentBrief, AgentDeps
from tavily import TavilyClient
import os
import asyncio
import argparse
import json

tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))


async def run_agent(company_name: str) -> InvestmentBrief | None:
    deps = AgentDeps(company_name=company_name, tavily_client=tavily_client)
    user_prompt = f'Produce an investment brief for {company_name}.'
    try:
        res = await agent.run(user_prompt=user_prompt, deps=deps)
        print(res.all_messages())
        return res.output
    except Exception as e:
        print(f'Error running agent: {e}')
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the investment research agent for a given company.')
    parser.add_argument('company_name', nargs='+', help='The name of the company to research')
    args = parser.parse_args()
    company_name = ' '.join(args.company_name)
    print(f'\nGenerating investment brief for {company_name}...\n')
    res = asyncio.run(run_agent(company_name))
    if not res:
        print('Failed to generate investment brief.')
    else:
        print(json.dumps(res.model_dump(), indent=2))
