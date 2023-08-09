# This is a sample Python script.
import asyncio
import icalendar
import discord
import requests
import re
from datetime import datetime, timedelta, time,date

from discord.ext import tasks


class Bin:
    def __init__(self, binType, date):
        self.bin = binType
        self.date = date


def getMoreBinDates():
    params = {
        'UPRN': 100060676634,
    }

    response = requests.get('https://www.southampton.gov.uk/whereilive/waste-calendar', params=params)

    ufprt = ""

    for lin in response.text.splitlines():
        if "ufprt" in lin:
            ufprt = re.search(r'(?<=value=").+(?=")', lin)
            break

    print(ufprt.group(0))

    data = {
        'ufprt': ufprt.group(0),
    }
    response2 = requests.post('https://www.southampton.gov.uk/whereilive/waste-calendar', params=params, data=data)
    return setUp(ical=response2.content)


def readICALFromFile():
    e = open("bins.ics", "rb")
    output = setUp(e.read())
    e.close()
    return output


def setUp(ical):
    # Use a breakpoint in the code line below to debug your script.
    binObjects = []
    ecal = icalendar.Calendar.from_ical(ical)
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

    return binObjects


timeToRun = time(hour=19, minute=51)

@tasks.loop(hours=24)
async def checkBins(client, bins):
    print("running")

    breakflag = True
    for bin in bins:
        if bin.date == datetime.now().date() + timedelta(0):
            channel = client.get_channel(628710600071053314)
            await channel.send("REMINDER : PUT OUT " + bin.bin + "!")
        if bin.date > datetime.now().date():
            breakflag = False
    if breakflag:
        checkBins.cancel()

@checkBins.after_loop
async def after_task():
    bins = getMoreBinDates()
    checkBins.start(client, bins)



@checkBins.before_loop
async def before_task():
    print("now")
    hour = 19
    minute = 59
    now = datetime.now()
    print(now)
    future = datetime(now.year, now.month, now.day, hour, minute)
    print(future)
    if now.hour >= hour and now.minute > minute:
        print("true")
        future += timedelta(days=1)
    print("running")
    await asyncio.sleep((future - now).seconds)


token = open(".token", "r").read()
intents = discord.Intents.default()

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    bins = getMoreBinDates()
    checkBins.start(client, bins)


client.run(token)
