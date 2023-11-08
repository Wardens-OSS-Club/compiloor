from typing import TypedDict


class ProtocolInformationConfigDict(TypedDict):
    title: str
    author: str
    date: str
    protocol_name: str
    repository: str
    type: str
    commit: str
    sloc: str
    about_author_content: str
    disclaimer_content: str
    about_protocol_content: str
    security_assessment_summary_content: str
    template_url: str
    stylesheet_url: str
    cover_img_url: str
    