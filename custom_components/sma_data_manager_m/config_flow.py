from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class SMADataManagerMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMA Data Manager M."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validation logic can go here
            return self.async_create_entry(
                title=f"SMA Data Manager ({user_input['host']})", data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required("host"): str,
                vol.Optional("username", default=""): str,
                vol.Optional("password", default=""): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
