from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JobSource:
    source_id: str
    name: str
    url: str
    employer: str
    default_location: str
    priority: int


@dataclass(frozen=True)
class JobItem:
    item_id: str
    title: str
    employer: str
    location: str
    employment_type: str
    contract_type: str
    pay_grade: str
    department: str
    deadline: str
    reference: str
    source_name: str
    source_url: str
    source_id: str
