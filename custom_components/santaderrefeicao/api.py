from typing import Dict
import aiohttp
import logging

from .lib import parseSessionState, parseOGCToken, parseCardDetails

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class SantanderRefeicaoAPI:
    """Interfaces to https://www.particulares.santander.pt/pagina/indice/0,,840_1_2,00.html"""
    
    def __init__(self, websession):
        self.websession = websession
        self._token = None
        self._cookie = None

    async def login(self, username, password) -> bool:
        """Issue LOGIN request."""
        try:
            _LOGGER.debug("Logging in...")

            session = await self._getSessionState()
            self._token = await self._getOGCToken()

            async with self.websession.post(
                "https://www.particulares.santander.pt/bepp/sanpt/usuarios/loginrefeicao/",
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data = {
                    "accion": 3,
                    f"{session['username']}": username,
                    f"{session['password']}": password,
                    "OGC_TOKEN": self._token
                }
            ) as res:
                if res.status == 200 and res.content_type == "text/html":
                    self._cookie = res.headers['set-cookie']
                    _LOGGER.debug("cookie", self._cookie)
                    return True
                return False
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)
            return False
    
    async def getAccountDetails(self) -> Dict[str, str]:
        """Issue ACCOUNT DETAILS request."""
        try:
            _LOGGER.debug("Fetch Account Details...")
            async with self.websession.get(
                "https://www.particulares.santander.pt/bepp/sanpt/tarjetas/listadomovimientostarjetarefeicao/0,,,0.shtml",
                headers = { 
                    'OGC_TOKEN': self._token 
                }
            ) as res:
                if res.status == 200 and res.content_type == "text/html":
                    html = await res.text()
                    cardDetails = parseCardDetails(html)
                    print ("cardDetails", cardDetails)
                    return {
                        'cardRef': cardDetails['cardRef'],
                        'grossBalance': float(cardDetails['grossBalance'].replace(' EUR', '').replace(",", ".")),
                        'netBalance': float(cardDetails['netBalance'].replace(' EUR', '').replace(",", "."))
                    }
                raise Exception("Could not retrieve account information from API")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)

    async def getMovementDetails(self, token):
        """Issue Movement Details request."""
        try:
            _LOGGER.debug("Fetch Movement Details...")
            async with self.websession.post(
                "https://www.particulares.santander.pt/bepp/sanpt/tarjetas/listadomovimientostarjetarefeicao",
                headers = { 
                    'Accept': 'text/html',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'OGC_TOKEN': token,
                },
                data = { 
                    'accion': 2 
                }
            ) as res:
                print (res)
                if res.status == 200 and res.content_type == "text/html":
                    html = await res.text()
                    print (html)
                    return None
                raise Exception("Could not retrieve movement details from API")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)

    async def getMovementDetailsExcel(self):
        """Issue Movement Details request."""
        try:
            _LOGGER.debug("Fetch Movement Details...")
            async with self.websession.post(
                "https://www.particulares.santander.pt/bepp/sanpt/tarjetas/listadomovimientostarjetarefeicao/0,,,00.xls",
                headers = { 
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html',
                    'cookie': self._cookie
                },
                data = { 
                    'accion': 3,
                    'formatoDescarga': 'xls',
                    'OGC_TOKEN': self._token
                }
            ) as res:
                print (res)
                if res.status == 200 and res.content_type == "text/html":
                    html = await res.text()
                    print (html)
                    return None
                raise Exception("Could not retrieve movement details from API")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)


    async def _getSessionState(self):
        try:
            _LOGGER.debug("Get Session State...")
            async with self.websession.get(
                "https://www.particulares.santander.pt/bepp/sanpt/usuarios/loginrefeicao/0,,,0.shtml"
            ) as res:
                if res.status == 200 and res.content_type == "text/html":
                    html = await res.text()
                    session = parseSessionState(html)
                    return session
                raise Exception("Could not retrieve token for user, login failed")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)

    async def _getOGCToken(self):
        try:
            _LOGGER.debug("Get OGC_TOKEN...")
            async with self.websession.post(
                "https://www.particulares.santander.pt/nbp_guard",
                headers = {'FETCH-CSRF-TOKEN': '1'}
            ) as res:
                if res.status == 200 and res.content_type == "text/plain":
                    text = await res.text()
                    token = parseOGCToken(text)
                    return token
                raise Exception("Could not retrieve token for user, login failed")
        except aiohttp.ClientError as err:
            _LOGGER.exception(err)