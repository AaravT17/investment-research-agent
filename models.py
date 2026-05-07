from pydantic import BaseModel
from typing import Optional, Literal
from dataclasses import dataclass
from tavily import TavilyClient


class KeyPerson(BaseModel):
    name: str
    role: str
    background: Optional[str] = None


class Competitor(BaseModel):
    company_name: str
    overview: str


class InvestmentBrief(BaseModel):
    company_name: str
    industry: str
    overview: str
    key_people: list[KeyPerson]
    funding_stage: Literal['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C', 'Series D+', 'Public', 'Unknown']
    total_funding: Optional[str] = None
    valuation: Optional[str] = None
    key_investors: Optional[list[str]] = None
    performance_summary: str
    analyst_rating: Optional[str] = None
    competitors: list[Competitor]
    risk_analysis: str
    recent_news: str
    recommendation: Literal['Strong Buy', 'Buy', 'Hold/Monitor', 'Avoid']
    recommendation_reasoning: str


@dataclass
class AgentDeps:
    company_name: str
    tavily_client: TavilyClient
