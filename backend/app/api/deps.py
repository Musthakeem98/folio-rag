from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.core.pipeline import IngestPipeline


def settings_dep() -> Settings:
    return get_settings()


def ingest_dep(request: Request) -> IngestPipeline:
    return request.app.state.ingest


SettingsDep = Depends(settings_dep)
IngestDep = Depends(ingest_dep)
