from i18n import get_base_path
import json
import os
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict


class LocalizationData(BaseModel):
    """Model representing localized strings and configuration for a specific language."""
    model_config = ConfigDict(populate_by_name=True)
    
    language_label: str = Field(alias="Language Label")
    application_name: str = Field(alias="Application Name")
    application_description: str = Field(alias="Application Description")


class TinoConfig(BaseModel):
    """Main configuration model for the Tino Uninstaller."""
    model_config = ConfigDict(populate_by_name=True)

    application_version: str = Field(alias="Application Version")
    application_author: str = Field(alias="Application Author")
    application_website: Optional[str] = Field(None, alias="Application Website")
    application_icon: str = Field(alias="Application Icon")

    application_installation_path: str = Field(alias="Application Installation Path")
    application_executable_path: str = Field(alias="Application Executable Path")
    application_icon_path: str = Field("", alias="Application Icon Path")
    application_desktop_path: str = Field("", alias="Application Desktop Path")
    application_pre_uninstallation_script: Optional[str] = Field(None, alias="Application Pre Uninstallation Script")
    application_post_uninstallation_script: Optional[str] = Field(None, alias="Application Post Uninstallation Script")
    application_name_slug: str = Field("", alias="Application Name Slug")
    application_uninstaller_desktop_path: str = Field("", alias="Application Uninstaller Desktop Path")
    application_uninstaller_icon_path: str = Field("", alias="Application Uninstaller Icon Path")

    localization: Dict[str, LocalizationData] = Field(alias="Localization")

    current_lang: str = "en_US"
    
    @property
    def local(self) -> LocalizationData:
        """Returns the localization data for the current language, with fallback to the first available."""
        if self.current_lang in self.localization:
            return self.localization[self.current_lang]
        return self.localization.get("en_US", next(iter(self.localization.values())))



def load_data() -> TinoConfig:
    """Finds and loads the uninstaller.tino configuration file."""
    config_file = os.path.join(get_base_path(), "uninstaller.tino")
    if not os.path.exists(config_file):
        raise RuntimeError("No uninstaller.tino configuration file found.")
    
    try:
        with open(config_file, encoding='utf-8') as f:
            data_dict = json.load(f)
    except Exception as e:
        raise RuntimeError(f"Failed to load {config_file}: {e}") from e

    config = TinoConfig(**data_dict)
    return config