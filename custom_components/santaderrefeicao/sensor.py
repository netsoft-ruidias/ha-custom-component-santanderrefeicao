"""Platform for sensor integration."""
from __future__ import annotations
from typing import Any
import aiohttp
import logging

from datetime import timedelta
from typing import Any, Callable, Dict

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD
)

from .api import SantanderRefeicaoAPI
from .const import (
    DOMAIN, COUNTRY, 
    DEFAULT_ICON, UNIT_OF_MEASUREMENT,
    ATTRIBUTION
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

# Time between updating data from API
SCAN_INTERVAL = timedelta(minutes=60)

async def async_setup_entry(hass: HomeAssistant, 
                            config_entry: ConfigEntry, 
                            async_add_entities: Callable):
    """Setup sensor platform."""
    session = async_get_clientsession(hass, True)
    api = SantanderRefeicaoAPI(session)

    config = config_entry.data
    sensors = [ SantanderSensor(api, config) ]
    async_add_entities(sensors, update_before_add=True)


class SantanderSensor(SensorEntity):
    """Representation of a Santander Refeicao Card (Sensor)."""

    def __init__(self, api: SantanderRefeicaoAPI, config: Any):
        super().__init__()
        self._api = api
        self._config = config
        self._cardRef = None
        self._grossBalance = None

        self._icon = DEFAULT_ICON
        self._unit_of_measurement = UNIT_OF_MEASUREMENT
        self._device_class = SensorDeviceClass.MONETARY
        self._state_class = SensorStateClass.TOTAL
        self._state = None
        self._available = False
        
    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return "Santander (Portugal) Cartão Refeição"

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return f"{DOMAIN}-{self._config[CONF_USERNAME]}-{COUNTRY}".lower()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> float:
        return self._state

    @property
    def device_class(self):
        return self._device_class

    @property
    def state_class(self):
        return self._state_class

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        return self._icon

    @property
    def attribution(self):
        return ATTRIBUTION

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        return {
            "CardRef": self._cardRef,
            "GrossBalance": self._grossBalance
        }

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        api = self._api
        config = self._config

        try:        
            login = await api.login(
                config[CONF_USERNAME], 
                config[CONF_PASSWORD])
            if (login):
                details = await api.getAccountDetails()
                self._state = details['netBalance']
                self._cardRef = details['cardRef']
                self._grossBalance = details['grossBalance']
                self._available = True

        except aiohttp.ClientError as err:
            self._available = False
            _LOGGER.exception("Error updating data from DGEG API.", err)            
