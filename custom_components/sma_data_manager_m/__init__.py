"""Initialize the SMA Data Manager M integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

import logging

_LOGGER = logging.getLogger(__name__)

# Ajout d'un try/except pour vérifier l'import de SMAApiClient
try:
    from .client import SMAApiClient
    _LOGGER.info("SMAApiClient imported successfully.")
except Exception as e:
    _LOGGER.error(f"Error importing SMAApiClient: {e}")

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SMA Data Manager M component."""
    _LOGGER.info("Setting up SMA Data Manager M component.")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SMA Data Manager M from a config entry."""
    _LOGGER.info(f"Setting up SMA Data Manager M entry for host {entry.data['host']}")

    hass.data.setdefault(DOMAIN, {})

    host = entry.data["host"]
    username = entry.data.get("username", "")
    password = entry.data.get("password", "")
    use_https = entry.data.get("use_https", False)

    _LOGGER.info(f"Host: {host}")
    _LOGGER.info(f"Username: {username}")
    _LOGGER.info(f"Use HTTPS: {use_https}")

    try:
        # Initialisation de SMAApiClient avec HTTPS ou HTTP
        client = SMAApiClient(host, username, password, use_ssl=use_https)
        _LOGGER.info("SMAApiClient initialized successfully.")
    except Exception as e:
        _LOGGER.error(f"Error initializing SMAApiClient: {e}")
        return False

    # Stockez le client dans les données partagées
    hass.data[DOMAIN][entry.entry_id] = client

    # Ajoutez les capteurs avec un await (correction du warning async_forward_entry_setup)
    try:
        await hass.config_entries.async_forward_entry_setup(entry, "sensor")
        _LOGGER.info("Sensor setup completed successfully.")
    except Exception as e:
        _LOGGER.error(f"Error during sensor setup: {e}")
        return False

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info(f"Unloading SMA Data Manager M entry for host {entry.data['host']}")
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
