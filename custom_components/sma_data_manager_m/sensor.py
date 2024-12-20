from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .client import SMAApiClient

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SMA Data Manager sensors."""
    host = config_entry.data["host"]
    username = config_entry.data.get("username", "")
    password = config_entry.data.get("password", "")

    # Initialize SMA client
    client = SMAApiClient(host, username, password, use_ssl=False)

    # Login and fetch initial data
    try:
        await client.login()
        components = await client.get_all_components()
    except Exception as e:
        _LOGGER.error(f"Failed to initialize SMA Data Manager: {e}")
        return

    # Create a sensor for each component
    entities = []
    for component in components:
        entities.append(SMASensor(client, component.name, component.component_id))

    async_add_entities(entities)


class SMASensor(SensorEntity):
    """Representation of an SMA sensor."""

    def __init__(self, client, name, component_id):
        """Initialize the sensor."""
        self._client = client
        self._name = name
        self._component_id = component_id
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            data = await self._client.get_live_measurements(
                [{"componentId": self._component_id}]
            )
            if data:
                self._state = data[0].value  # Adjust based on API response structure
        except Exception as e:
            _LOGGER.error(f"Failed to update sensor {self._name}: {e}")
            self._state = None
