from pydantic import BaseModel
from typing import Literal


class ClassifiedContent(BaseModel):
    url: str
    section : Literal["installation", "getting_started", "features"]
    raw_text: str
    source_title: str


class OrganisedDocs(BaseModel):
    installation: list[ClassifiedContent]
    getting_started: list[ClassifiedContent]
    features: list[ClassifiedContent]



