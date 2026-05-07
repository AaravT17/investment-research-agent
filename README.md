# Investment Research Agent

A CLI tool that generates structured investment briefs for any company — public or private — using an AI agent backed by Claude Sonnet, real-time web search, and live market data.

## Overview

Given a company name, the agent researches the company using web search and financial data APIs, then produces a structured investment brief covering the company's overview, financials, key people, competitors, risk factors, recent news, and a final investment recommendation (Strong Buy / Buy / Hold/Monitor / Avoid).

Output can be printed directly to the terminal as formatted markdown, or saved to a folder containing a `report.md` and a full `agent_message_history.json` for auditability.

## Features

- Works for **public and private companies** — uses yfinance for live market data on public companies, falls back to web search for private ones
- **Structured output** via Pydantic models — every brief has the same consistent schema
- **Four-tier recommendation**: Strong Buy, Buy, Hold/Monitor, or Avoid with full reasoning
- **Dual output modes**: rich terminal display or saved files
- **Full observability**: agent message history saved alongside the report so you can inspect every tool call and LLM response
- **Deterministic analysis**: temperature set to 0.0 for consistent, reliable financial reasoning

## Prerequisites

- Python 3.10+
- A [Tavily API key](https://app.tavily.com/)
- An API key for your chosen LLM provider (default: Anthropic)

> **Note:** The agent is built on pydantic-ai, so any [supported model provider](https://ai.pydantic.dev/models/) (OpenAI, Gemini, Groq, Mistral, and more) works — not just Anthropic. To switch, update the model and API key in `agent.py` and `.env`.

## Installation

```bash
git clone https://github.com/AaravT17/investment-research-agent.git
cd investment-research-agent

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install "pydantic-ai[anthropic]" yfinance tavily-python rich python-dotenv
```

## Configuration

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=your_anthropic_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## Usage

```bash
# Single-word company name — prints report to terminal
python main.py Apple

# Multi-word company name
python main.py Berkshire Hathaway

# Save report and message history to a folder
python main.py Tesla --output ~/Desktop
```

### `--output` flag

When provided, results are saved to `{output}/{company_name}_investment_brief/` containing:

```
tesla_investment_brief/
├── report.md                   # Formatted markdown investment brief
└── agent_message_history.json  # Full agent conversation log (tool calls + LLM responses)
```

If omitted, the report is printed to the terminal using rich formatting.

## Output Format

Every investment brief includes:

| Section             | Description                                                             |
| ------------------- | ----------------------------------------------------------------------- |
| Overview            | Company summary, industry, funding stage                                |
| Key People          | Names, roles, and backgrounds                                           |
| Financials          | Valuation, funding, investors, or live market data for public companies |
| Performance Summary | Revenue, growth, margins, analyst ratings                               |
| Competitors         | Key competitors with brief overviews                                    |
| Risk Analysis       | Key risk factors                                                        |
| Recent News         | Relevant news from the past year                                        |
| Recommendation      | Strong Buy / Buy / Hold/Monitor / Avoid + reasoning                     |

## Project Structure

```
investment-research-agent/
├── main.py       # CLI entry point and argument parsing
├── agent.py      # pydantic-ai agent definition and tool implementations
├── models.py     # Pydantic output schema (InvestmentBrief, KeyPerson, Competitor)
├── display.py    # Markdown rendering and file saving
└── .env          # API keys (not committed)
```

## How It Works

1. `main.py` parses the CLI arguments and invokes the agent
2. The agent (`claude-sonnet-4-5`) receives a system prompt instructing it to act as an investment research analyst and never rely on training data
3. It calls its tools autonomously to gather information:
   - `get_general_info` — Tavily web search for company overview, key people, competitors
   - `get_financial_data` — yfinance for live market data (public companies only, with 2 retries for ticker correction)
   - `get_financial_info` — Tavily finance search for private company financials or anything unavailable via yfinance
   - `get_recent_news_summary` — Tavily news search scoped to the past year
4. The agent's output is validated against the `InvestmentBrief` Pydantic schema
5. `display.py` renders the structured output as markdown for the terminal or saves it to disk
