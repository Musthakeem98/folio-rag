"""Web page parser: fetch → trafilatura extraction → markdown.

trafilatura handles boilerplate removal and emits clean markdown; it's
noticeably better than readability-lxml + markdownify for most news/blog
content and comparable on docs sites.
"""

from dataclasses import dataclass, field

import httpx


@dataclass
class WebParsed:
    source: str
    markdown: str
    pages: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class WebParser:
    name = "web"

    def __init__(self, timeout: float = 30.0, user_agent: str = "Folio/0.0 (+github)"):
        self.timeout = timeout
        self.user_agent = user_agent

    async def parse(self, source: str) -> WebParsed:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers={"user-agent": self.user_agent},
            follow_redirects=True,
        ) as client:
            r = await client.get(source)
            r.raise_for_status()
            html = r.text

        import trafilatura

        md = trafilatura.extract(
            html,
            url=source,
            output_format="markdown",
            include_tables=True,
            include_links=False,
            favor_recall=True,
        ) or ""

        meta: dict = {}
        extracted_meta = trafilatura.extract_metadata(html)
        if extracted_meta is not None:
            as_dict = extracted_meta.as_dict() if hasattr(extracted_meta, "as_dict") else {}
            meta = {k: v for k, v in as_dict.items() if v}

        return WebParsed(source=source, markdown=md, metadata=meta)
