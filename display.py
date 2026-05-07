from rich.console import Console
from rich.markdown import Markdown
from models import InvestmentBrief
from pydantic_ai import AgentRunResult
import os

console = Console()


def build_markdown(brief: InvestmentBrief) -> str:
    md = f'# {brief.company_name}\n\n'
    md += f'**Industry:** {brief.industry} | **Funding Stage:** {brief.funding_stage}\n\n'
    md += f'## Overview\n{brief.overview}\n\n'

    if brief.key_people:
        md += '## Key People\n'
        for person in brief.key_people:
            md += f'- **{person.name}** — {person.role}'
            if person.background:
                md += f': {person.background}'
            md += '\n'
        md += '\n'

    financials = ''
    if brief.valuation:
        financials += f'- **Valuation:** {brief.valuation}\n'
    if brief.total_funding:
        financials += f'- **Total Funding:** {brief.total_funding}\n'
    if brief.key_investors:
        financials += f'- **Key Investors:** {", ".join(brief.key_investors)}\n'
    if brief.analyst_rating:
        financials += f'- **Analyst Rating:** {brief.analyst_rating}\n'

    if financials:
        md += f'## Financials\n{financials}\n'

    md += f'## Performance Summary\n{brief.performance_summary}\n\n'

    if brief.competitors:
        md += '## Competitors\n'
        for competitor in brief.competitors:
            md += f'- **{competitor.company_name}:** {competitor.overview}\n'
        md += '\n'

    md += f'## Risk Analysis\n{brief.risk_analysis}\n\n'
    md += f'## Recent News\n{brief.recent_news}\n\n'
    md += f'## Recommendation: {brief.recommendation}\n{brief.recommendation_reasoning}\n'

    return md


def print_brief(brief: InvestmentBrief) -> None:
    md = build_markdown(brief)
    console.print(Markdown(md))


def save_brief(res: AgentRunResult[InvestmentBrief], parent_dir: str) -> None:
    try:
        # use company name to create a unique folder for each brief, use name from the brief output to prevent
        # issues due to user input errors
        dir_path = os.path.join(
            parent_dir,
            f'{res.output.company_name.lower().replace(" ", "_")}_investment_brief',
        )
        os.makedirs(dir_path, exist_ok=True)

        md = build_markdown(res.output)

        report_filepath = os.path.join(dir_path, 'report.md')
        with open(report_filepath, 'w') as f:
            f.write(md)
        print(f'Investment brief saved to {report_filepath}')

        msg_history_filepath = os.path.join(dir_path, 'agent_message_history.json')
        with open(
            msg_history_filepath, 'wb'
        ) as f:  # since all_messages_json returns bytes, we need to write in binary mode
            f.write(res.all_messages_json())
        print(f'Agent message history saved to {msg_history_filepath}')
    except Exception as e:
        print(f'Error creating directory for investment brief: {e}')
        print_brief(res.output)
