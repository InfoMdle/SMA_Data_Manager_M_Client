import json
import asyncio
import datetime
import time

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

    last = 0

    while True:
        for measurement in await api.get_all_live_measurements(["Plant:1"]):
            if measurement.channel_id == "Measurement.GridMs.TotW.Pv" and measurement.latest_value().value != last:
                print(f"{measurement.latest_value().time} : {measurement.channel_id} - {measurement.latest_value().value}")
                last = measurement.latest_value().value

                f = open("log.txt", "a")
                f.write(f"{measurement.latest_value().time},{measurement.channel_id},{measurement.latest_value().value}\n")
                f.close()

        time.sleep(1)


asyncio.run(testfunction())