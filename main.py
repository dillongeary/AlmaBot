# This is a sample Python script.
import asyncio
import icalendar
import discord
from datetime import datetime, timedelta

from discord.ext import tasks


class Bin:
    def __init__(self, binType, date):
        self.bin = binType
        self.date = date


def setUp():
    # Use a breakpoint in the code line below to debug your script.
    binObjects = []
    e = open("bins.ics", "rb")
    ecal = icalendar.Calendar.from_ical(e.read())
    for component in ecal.walk():
        if component.name == "VEVENT":
            binType = component.get("SUMMARY")
            match binType:
                case "HOUSEHOLD":
                    binPrint = "GENERAL WASTE"
                case other:
                    binPrint = binType + " BIN"
            binDate = component.decoded("dtstart")
            binObjects.append(Bin(binPrint, binDate))
    e.close()

    return binObjects


@tasks.loop(hours=24)
async def checkBins(client, bins):
    print("running")
    for bin in bins:
        if bin.date == datetime.now().date() + timedelta(0):
            channel = client.get_channel(628710600071053314)
            await channel.send("REMINDER : PUT OUT " + bin.bin + "!")


# Press the green button in the gutter to run the script.


token = open(".token","r").read()
intents = discord.Intents.default()

client = discord.Client(intents=intents)


@checkBins.before_loop
async def before_task():
    print("now")
    hour = 00
    minute = 47
    now = datetime.now()
    print(now)
    future = datetime(now.year, now.month, now.day, hour, minute)
    print(future)
    if now.hour >= hour and now.minute > minute:
        print("true")
        future += timedelta(days=1)
    print("running")
    await asyncio.sleep((future - now).seconds)


@client.event
async def on_ready():
    bins = setUp()
    checkBins.start(client, bins)


client.run(token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
