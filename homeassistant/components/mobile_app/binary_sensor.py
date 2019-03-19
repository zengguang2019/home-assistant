"""Binary sensor platform for mobile_app."""
from functools import partial

from homeassistant.const import CONF_WEBHOOK_ID
from homeassistant.core import callback
from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import (ATTR_SENSOR_STATE,
                    ATTR_SENSOR_TYPE_BINARY_SENSOR as ENTITY_TYPE,
                    DATA_DEVICES, DATA_SIGNAL_HANDLES, DOMAIN)

from .entity import MobileAppEntity

DEPENDENCIES = ['mobile_app']


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up mobile app binary sensor from a config entry."""
    entities = list()

    webhook_id = config_entry.data[CONF_WEBHOOK_ID]

    for config in hass.data[DOMAIN][ENTITY_TYPE].values():
        if config[CONF_WEBHOOK_ID] != webhook_id:
            continue

        device = hass.data[DOMAIN][DATA_DEVICES][webhook_id]

        entities.append(MobileAppBinarySensor(config, device, config_entry))

    async_add_entities(entities)

    @callback
    def handle_sensor_registration(webhook_id, data):
        if data[CONF_WEBHOOK_ID] != webhook_id:
            return

        device = hass.data[DOMAIN][DATA_DEVICES][data[CONF_WEBHOOK_ID]]

        async_add_entities([MobileAppBinarySensor(data, device, config_entry)])

    handles = hass.data[DOMAIN][DATA_SIGNAL_HANDLES][ENTITY_TYPE]
    handles[webhook_id] = \
        async_dispatcher_connect(hass,
                                 '{}_{}_register'.format(DOMAIN, ENTITY_TYPE),
                                 partial(handle_sensor_registration,
                                         webhook_id))


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    handles = hass.data[DOMAIN][DATA_SIGNAL_HANDLES][ENTITY_TYPE]
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    handles[webhook_id]()


class MobileAppBinarySensor(MobileAppEntity, BinarySensorDevice):
    """Representation of an mobile app binary sensor."""

    @property
    def is_on(self):
        """Return the state of the binary sensor."""
        return self._config[ATTR_SENSOR_STATE]
