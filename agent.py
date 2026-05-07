from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic_ai.models.anthropic import AnthropicModel
from models import InvestmentBrief, AgentDeps
import yfinance as yf
import json

model = AnthropicModel('claude-sonnet-4-5')

system_prompt = """You are an investment research analyst. Given a company name, produce a thorough and accurate investment brief.

Always use your tools to gather information. Never rely on your training data, as it may be outdated/incomplete/inaccurate, especially for private companies.
- Use the get_general_info tool for general information about the company, such as its products and services, key people, and competitors
- Use get_financial_data for publicly traded companies, and get_financial_info for private companies or anything not available via get_financial_data
- Use get_recent_news_summary to gather recent news about the company, with a focus on topics relevant to financial performance and investment potential

If you cannot find information about the company after using your tools, it is better to leave fields blank or write 'No information found' rather than making up information. Optional fields (total_funding, valuation, key_investors, analyst_rating) may be left null if the information is genuinely unavailable after searching."""

agent = Agent(
    model=model,
    deps_type=AgentDeps,
    output_type=InvestmentBrief,
    model_settings=ModelSettings(
        max_tokens=8000,
        temperature=0.2,
        # for financial analysis, we want consistency and reliability, so a lower temperature is appropriate
    ),
    system_prompt=system_prompt,
)


@agent.tool
async def get_general_info(ctx: RunContext[AgentDeps], query: str, detailed: bool) -> str:
    """
    Perform a web search to gather general information about the company.
    Provide the company name in the query, along with any specific information you want to find out about the company.
    This tool is for gathering general information about the company, such as its products and services, key people,
    and competitors. For financial information, use the get_financial_data tool or the get_financial_info tool instead.
    Set 'detailed' to True if the query requires more detailed information about the company, such as information
    about its competitors, and False if the query is more straightforward/factual and only requires basic information
    about the company.
    Example queries:
        - "What are the key products and services offered by {company_name}?",
        - "Who are the main competitors of {company_name}?"
    """
    try:
        res = ctx.deps.tavily_client.search(
            query, topic='general', max_results=5, include_answer='advanced' if detailed else 'basic'
        )

        if not res.get('answer'):
            return 'No information found.'

        return res['answer']
    except Exception as e:
        print(f'Error fetching general info: {e}')
        return 'Could not fetch the information.'


@agent.tool
async def get_financial_info(ctx: RunContext[AgentDeps], query: str) -> str:
    """
    Perform a web search to gather financial information about the company.
    Provide the company name in the query, along with any specific information you want to find out about the company.
    Use this tool to gather financial information about the company that is not available through the get_financial_data
    tool, or if the company is not publicly traded and therefore does not have a stock ticker symbol.
    Example queries:
        - "What is the annual revenue of {company_name}?",
        - "What is the funding history of {company_name}?",
        - "Who are the key investors in {company_name}?"
    """
    try:
        res = ctx.deps.tavily_client.search(query, topic='finance', max_results=5, include_answer='advanced')

        if not res.get('answer'):
            return 'No information found.'

        return res['answer']
    except Exception as e:
        print(f'Error fetching financial info: {e}')
        return 'Could not fetch the information.'


@agent.tool(retries=2)
async def get_financial_data(ctx: RunContext[AgentDeps], ticker_symbol: str) -> str:
    """
    Fetch financial data for a publicly traded company using its stock ticker symbol.
    Only use this tool if the company is publicly traded and you know its ticker symbol.
    Input should be the ticker symbol e.g. 'NVDA', 'AAPL', 'GOOGL', not the full company name.
    Returns a JSON string with the following fields:
        - market_cap
        - total_revenue
        - revenue_growth
        - profit_margins
        - trailing_pe
        - current_price
        - earnings_growth
        - free_cashflow
        - full_time_employees
        - analyst_count
        - recommendation
    """
    ticker = yf.Ticker(ticker_symbol)
    ticker_info = ticker.info

    if not ticker_info.get('symbol', None) and not ticker_info.get('shortName', None):
        raise ModelRetry(
            f'No financial data found for ticker symbol "{ticker_symbol}". Please check that the ticker symbol is the correct ticker symbol for {ctx.deps.company_name}. If the company is not publicly traded, do not use this tool and instead gather information using the get_financial_info tool. If you are not sure if the company is publicly traded or what its ticker symbol is, use the get_general_info tool to find out.',
        )
        # 2 retries should be sufficient for the model to correct the ticker symbol or realize that the company is not
        # publicly traded and switch to using the get_financial_info tool instead

    financial_data = {
        'market_cap': ticker_info.get('marketCap'),
        'total_revenue': ticker_info.get('totalRevenue'),
        'revenue_growth': ticker_info.get('revenueGrowth'),
        'profit_margins': ticker_info.get('profitMargins'),
        'trailing_pe': ticker_info.get('trailingPE'),
        'current_price': ticker_info.get('currentPrice'),
        'earnings_growth': ticker_info.get('earningsGrowth'),
        'free_cashflow': ticker_info.get('freeCashflow'),
        'full_time_employees': ticker_info.get('fullTimeEmployees'),
        'analyst_count': ticker_info.get('numberOfAnalystOpinions'),
        'recommendation': ticker_info.get('recommendationKey'),
    }

    return json.dumps(financial_data)


@agent.tool
async def get_recent_news_summary(ctx: RunContext[AgentDeps]) -> str:
    """
    Fetch recent news about the company.
    Use this tool to gather recent news about the company, with a focus on topics relevant to financial performance
    and investment potential.
    """
    try:
        res = ctx.deps.tavily_client.search(
            f'Recent news about {ctx.deps.company_name}, with a focus on topics relevant to financial performance and investment potential.',
            topic='news',
            time_range='year',
            max_results=5,
            include_answer='advanced',
        )

        if not res.get('answer'):
            return 'No information found.'

        return res['answer']
    except Exception as e:
        print(f'Error fetching recent news summary: {e}')
        return 'Could not fetch recent news summary.'
