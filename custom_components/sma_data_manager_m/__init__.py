"""Initialize the SMA Data Manager M integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .client import SMAApiClient  # Importez correctement la classe

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SMA Data Manager M component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SMA Data Manager M from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    username = entry.data.get("username", "")
    password = entry.data.get("password", "")
    use_https = entry.data.get("use_https", False)  # Récupérer le paramètre HTTPS

    # Initialisez le client SMA avec l'option HTTPS
    client = SMAApiClient(host, username, password, use_ssl=use_https)

    # Stockez le client dans les données partagées
    hass.data[DOMAIN][entry.entry_id] = client

    # Ajoutez les capteurs
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
