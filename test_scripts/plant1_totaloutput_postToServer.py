import json
import asyncio
import requests
import time

from SmaDataManagerMClient.client import SMAApiClient

sourceSystem = "Bauer1"

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
            if measurement.channel_id == "Measurement.GridMs.TotW.Pv" and measurement.latest_value().time != last:
                print(f"{measurement.latest_value().time} : {measurement.channel_id} - {measurement.latest_value().value}")
                last = measurement.latest_value().time

                f = open("log.txt", "a")
                f.write(f"{measurement.latest_value().time},{measurement.channel_id},{measurement.latest_value().value}\n")
                f.close()

                requests.post(url='http://192.168.90.231:7500/api/insertEnergy',
                              json= {
                                    "sourceSystem": sourceSystem,
                                    "dataType": "production",
                                    "energyValue": measurement.latest_value().value,
                                    "timestamp": measurement.latest_value().time
                                })

        time.sleep(1)

asyncio.run(testfunction())