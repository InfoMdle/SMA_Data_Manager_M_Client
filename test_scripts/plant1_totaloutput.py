import json
import asyncio

from SmaDataManagerMClient.client import SMAApiClient

async def testfunction():
    cred = json.load(open("credentials.json"))

    print(cred["email"])
    print(cred["password"])

    api = SMAApiClient(
        host="192.168.1.169",
        username=cred["email"],
        password=cred["password"]
    )

    await api.login()

    ids = []

    for component in await api.get_all_components():
        ids.append(component.component_id)

    print(await api.get_all_live_measurements(["Plant:1"]))

asyncio.run(testfunction())