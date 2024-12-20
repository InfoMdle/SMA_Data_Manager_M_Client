from homeassistant.components.sensor import SensorEntity
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from .const import DOMAIN
from .client import SMAApiClient

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up SMA Data Manager sensors."""
    # Initialize hass.data for the domain if not already done
    hass.data.setdefault(DOMAIN, {})

    # Check if this config_entry is already configured
    if config_entry.entry_id in hass.data[DOMAIN]:
        _LOGGER.warning(
            f"Config entry {config_entry.title} ({config_entry.entry_id}) for {DOMAIN} has already been set up!"
        )
        return

    # Mark this config_entry as configured
    hass.data[DOMAIN][config_entry.entry_id] = True

    host = config_entry.data[CONF_HOST]
    username = config_entry.data.get(CONF_USERNAME, "")
    password = config_entry.data.get(CONF_PASSWORD, "")
    use_https = config_entry.data.get("use_https", False)

    # Initialize SMA client
    client = SMAApiClient(host, username, password, use_ssl=use_https)
    _LOGGER.info(f"Initializing SMAApiClient for host {host} with HTTPS={use_https}")

    # Login and fetch initial data
    try:
        await client.login()
        components = await client.get_all_components()
        _LOGGER.info(f"Fetched {len(components)} components from SMA Data Manager.")
    except Exception as e:
        _LOGGER.error(f"Failed to initialize SMA Data Manager: {e}")
        return

    # Create a sensor for each component
    entities = []
    for component in components:
        if "name" in component and "component_id" in component:
            entities.append(SMASensor(client, component["name"], component["component_id"]))
        else:
            _LOGGER.warning(f"Skipping component with missing data: {component}")

    _LOGGER.info(f"Adding {len(entities)} sensors to Home Assistant.")
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

    @property
    def unique_id(self):
        """Return a unique ID for the sensor."""
        return f"{self._client.host}_{self._component_id}"

    @property
    def should_poll(self):
        """Indicate that updates are handled via async_update."""
        return False

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            data = await self._client.get_live_measurements(
                [{"componentId": self._component_id}]
            )
            if data and isinstance(data, list) and "value" in data[0]:
                self._state = data[0]["value"]
                _LOGGER.debug(f"Updated sensor {self._name}: {self._state}")
            else:
                _LOGGER.warning(f"Unexpected data format for sensor {self._name}: {data}")
                self._state = None
        except Exception as e:
            _LOGGER.error(f"Failed to update sensor {self._name}: {e}")
            self._state = None
