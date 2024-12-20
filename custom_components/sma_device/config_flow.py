import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

class SMADeviceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMA Device."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            try:
                await self._test_connection(
                    user_input["host"],
                    user_input["username"],
                    user_input["password"],
                    user_input["use_https"],
                    user_input["allow_invalid_cert"],
                )
                return self.async_create_entry(title="SMA Device", data=user_input)
            except Exception as e:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Optional("use_https", default=True): bool,
                vol.Optional("allow_invalid_cert", default=False): bool,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def _test_connection(self, host, username, password, use_https, allow_invalid_cert):
        """Test the connection to the API."""
        protocol = "https" if use_https else "http"
        url = f"{protocol}://{host}/api/v1/token"
        session = async_get_clientsession(self.hass)

        try:
            async with session.post(
                url,
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                ssl=not allow_invalid_cert,
            ) as response:
                if response.status != 200:
                    raise Exception("Invalid response")
        except Exception as e:
            raise e
