import aiohttp
import asyncio
import time
from csv import writer
from datetime import date, datetime

today = date.today()
now = datetime.now()
open_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
close_time = now.replace(hour=15, minute=15, second=0, microsecond=0)
start_time = time.time()
failed_list = []
retries = 3

url = "https://analytics2.rti.co.id/queryStock_json.jsp"
headers = {
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Language': 'en-GB,en;q=0.9,id-ID;q=0.8,id;q=0.7,en-US;q=0.6',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Cookie': 'JSESSIONID=957CC52B39C1B815A62A181B2C041246.worker1; JSESSIONID=19C09004C371B1628355B303B340A851.worker1; JSESSIONID=664BD32043B7B2E61ECF22B26C666025.worker1',
  'Origin': 'https://analytics2.rti.co.id',
  'Referer': 'https://analytics2.rti.co.id/?m_id=1&sub_m=s2',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Linux"'
}

stocks = [
    "ABMM",
    "ACES",
    "ACST",
    "ADHI",
    "ADMR",
    "ADRO",
    "AGII",
    "AGRO",
    "AGRS",
    "AKSI",
    "ALTO",
    "AMAR",
    "ANDI",
    "ANTM",
    "APIC",
    "APLN",
    "ARCI",
    "ARMY",
    "ARTO",
    "ASJT",
    "ASRI",
    "AUTO",
    "BACA",
    "BALI",
    "BBCA",
    "BBHI",
    "BBKP",
    "BBTN",
    "BBYB",
    "BCAP",
    "BCIP",
    "BDMN",
    "BEBS",
    "BEEF",
    "BEST",
    "BFIN",
    "BGTG",
    "BIKA",
    "BINA",
    "BINO",
    "BIRD",
    "BJBR",
    "BKDP",
    "BKSL",
    "BKSW",
    "BMTR",
    "BNBA",
    "BNBR",
    "BOGA",
    "BOLA",
    "BOSS",
    "BRIS",
    "BRPT",
    "BSSR",
    "BTPN",
    "BUMI",
    "CARS",
    "CBMF",
    "CENT",
    "CFIN",
    "CINT",
    "CLEO",
    "CMNP",
    "CMNT",
    "CMPP",
    "COWL",
    "DAYA",
    "DEAL",
    "DEPO",
    "DGIK",
    "DIGI",
    "DILD",
    "DNAR",
    "DOID",
    "DSFI",
    "EMTK",
    "ESSA",
    "ESTA",
    "EXCL",
    "FILM",
    "FITT",
    "FORZ",
    "GJTL",
    "GOOD",
    "HEAL",
    "HOKI",
    "HOME",
    "HOMI",
    "HRME",
    "HRTA",
    "HRUM",
    "ICON",
    "IIKP",
    "IKAI",
    "IKAN",
    "INAF",
    "INCO",
    "INDF",
    "INDY",
    "IPCC",
    "IPCM",
    "IRRA",
    "ISAT",
    "ISSP",
    "ITIC",
    "JAWA",
    "JGLE",
    "JPFA",
    "JSKY",
    "JSMR",
    "JTPE",
    "KAEF",
    "KBAG",
    "KBLI",
    "KINO",
    "KKGI",
    "KLBF",
    "KPAS",
    "KPIG",
    "KREN",
    "LABA",
    "LINK",
    "LPKR",
    "LPPF",
    "MAIN",
    "MAMI",
    "MARK",
    "MBSS",
    "MCAS",
    "MDLN",
    "MEDC",
    "META",
    "MGNA",
    "MGRO",
    "MKPI",
    "MLBI",
    "MLIA",
    "MLPL",
    "MLPT",
    "MMLP",
    "MPOW",
    "MPPA",
    "MSIN",
    "MTDL",
    "MYOR",
    "MYRX",
    "NIKL",
    "NIRO",
    "NOBU",
    "OKAS",
    "PNBS",
    "POLL",
    "PSKT",
    "PTPP",
    "PTPW",
    "PTRO",
    "PURA",
    "PYFA",
    "RALS",
    "REAL",
    "RIMO",
    "RMKE",
    "SBMA",
    "SHIP",
    "SIDO",
    "SILO",
    "SIMA",
    "SIMP",
    "SLIS",
    "SMCB",
    "SMDR",
    "SMGR",
    "SMRU",
    "SMSM",
    "SPTO",
    "SQMI",
    "SRIL",
    "SRTG",
    "SSIA",
    "TAMU",
    "TCPI",
    "TDPM",
    "TECH",
    "TELE",
    "TINS",
    "TMAS",
    "TNCA",
    "TOWR",
    "TOYS",
    "TPIA",
    "TRIS",
    "UFOE",
    "UNSP",
    "UNVR",
    "VOKS",
    "WEHA",
    "WIKA",
    "WOOD",
    "YELO",
    "ZYRX",
]

async def request(session, stock):
    payload = "kode=" + stock
    async with session.get(url, data=payload, headers=headers) as response:
        result = await response.json()
        if response.status == 200:
            yahoo_stock = stock + ".JK"
            detail = result['stk_detail']
            open = detail['open_price']
            high = detail['high_price']
            low = detail['low_price']
            close = detail['last_price']
            volume = detail['last_vol']
            date = today.strftime("%d/%m/%Y")
            new_row = [yahoo_stock, date, open, high, low, close, volume]
            append(new_row)
        else:
            n = 0
            while n <= retries:
                request(session, stock)
                n += 1

async def perform_session():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for stock in stocks:
            tasks.append(asyncio.ensure_future(request(session, stock)))

        gathered_tasks = await asyncio.gather(*tasks)
        for task in gathered_tasks:
            if task != None:
                print(task.result())

async def main():
    while now >= open_time and now <= close_time:
        await perform_session()
        time.sleep(60)

    # For testing
    # n = 0
    # while n <= 10:
    #     await perform_session()
    #     time.sleep(60)
    #     n += 1
    #     print("Retry: " + n)

    print("Market is closed")

def append(element_to_append):
    with open(r"/Users/gamarinaldi/Desktop/sandbox/market_data.csv", 'a+', newline='') as append_obj:
        append_writer = writer(append_obj)
        append_writer.writerow(element_to_append)

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))
