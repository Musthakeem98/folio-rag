from fastapi import Depends

from lumen.config import Settings, get_settings


def settings_dep() -> Settings:
    return get_settings()


SettingsDep = Depends(settings_dep)
