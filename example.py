import asyncio
import aiohttp

from custom_components.santaderrefeicao.api import SantanderRefeicaoAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = SantanderRefeicaoAPI(session)

        username = input("Enter your Card Number.......: ") 
        password = input("Enter the Verification Code..: ") 

        login = await api.login(username, password)
        if login:
            details = await api.getAccountDetails()
            print("     Card Ref........:", details['cardRef'])
            print("     Gross Balance...:", details['grossBalance'])
            print("     Net Balance.....:", details['netBalance'])
            print("     ")

            movs = await api.getMovementDetailsExcel()
            print("     MOVS............:", movs)
        
asyncio.get_event_loop().run_until_complete(main())