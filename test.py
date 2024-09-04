import json
import asyncio

from SmaDataManagerMClient.client import SMAApiClient

async def testfunction():
    cred = json.load(open("credentials.json"))

    api = SMAApiClient(
        host="192.168.1.169",
        username=cred["email"],
        password=cred["password"]
    )

    try:
        await api.login()
    except:
        exit()

    print(json.dumps( await api.get_all_live_measurements(), indent=4 ))

asyncio.run(testfunction())