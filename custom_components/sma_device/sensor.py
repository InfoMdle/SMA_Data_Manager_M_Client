import logging
import aiohttp
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = 60  # seconds


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up sensors dynamically based on API response."""
    config = entry.data

    coordinator = SMADeviceDataUpdateCoordinator(hass, config)
    await coordinator.async_config_entry_first_refresh()

    # Create sensors dynamically based on API data
    entities = []
    for channel_id, channel_data in coordinator.data.items():
        entities.append(SMADeviceSensor(coordinator, channel_id, channel_data["name"]))

    async_add_entities(entities)


class SMADeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, config):
        """Initialize the data coordinator."""
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)
        self.config = config
        self.session = aiohttp.ClientSession()

    async def _async_update_data(self):
        """Fetch data from the API."""
        try:
            protocol = "https" if self.config["use_https"] else "http"
            url = f"{protocol}://{self.config['host']}/api/v1/measurements/live"
            payload = [{"componentId": "Plant:1"}]

            # Authenticate and fetch token
            token = await self._fetch_access_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            async with self.session.post(url, json=payload, headers=headers, ssl=not self.config["allow_invalid_cert"]) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Error fetching data: {response.status}")
                data = await response.json()

            # Format data into a dictionary for sensors
            return {
                item["channelId"]: {
                    "name": item["channelId"],
                    "value": item["values"][0]["value"],
                }
                for item in data if "values" in item and item["values"]
            }

        except Exception as e:
            raise UpdateFailed(f"Error communicating with API: {e}")

    async def _fetch_access_token(self):
        """Fetch the access token from the API."""
        protocol = "https" if self.config["use_https"] else "http"
        url = f"{protocol}://{self.config['host']}/api/v1/token"

        try:
            async with self.session.post(
                url,
                data={
                    "grant_type": "password",
                    "username": self.config["username"],
                    "password": self.config["password"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                ssl=not self.config["allow_invalid_cert"],
            ) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch token")
                result = await response.json()
                return result.get("access_token")
        except Exception as e:
            raise Exception(f"Error fetching access token: {e}")


class SMADeviceSensor(Entity):
    """Representation of an SMA Device Sensor."""

    def __init__(self, coordinator, channel_id, name):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.channel_id = channel_id
        self._name = name
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.data[self.channel_id]["value"]

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"sma_{self.channel_id}"

    async def async_update(self):
        """Update the sensor state."""
        await self.coordinator.async_request_refresh()
