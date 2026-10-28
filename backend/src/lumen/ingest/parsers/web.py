"""Web page parser: fetch → clean → markdown."""

from dataclasses import dataclass, field


@dataclass
class WebParsed:
    source: str
    markdown: str
    pages: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class WebParser:
    name = "web"

    async def parse(self, source: str) -> WebParsed:
        # TODO: httpx fetch + readability + markdownify
        return WebParsed(source=source, markdown="")
