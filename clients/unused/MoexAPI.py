# MoexAPI.py
import api.abstract as _a
import requests
import time
import enum

# https://iss.moex.com/iss/index
# https://iss.moex.com/iss/securities/IMOEX.xml
# https://ftp.moex.com/pub/ClientsAPI/ASTS/Bridge_Interfaces/MarketData/Currency37_Info_English.htm

"""
class MoexIndexEnum(enum.IntEnum):
    SECID                           = 0     # Код индекса
    SHORTNAME                       = 2     # Краткое наименование индекса
    NAME                            = 3     # Полное наименование
    LATNAME                         = 5     # Английское наименование
    CURRENCYID                      = 8     # Валюта расчета
    FREQUENCY                       = 9     # Режим расчета
    INITIALVALUE                    = 12    # Начальное значение индекса
    ISSUEDATE                       = 13    # Дата начала публикации
    INITIALCAPITALIZATION           = 15    # Начальная капитализация
    INITIALD                        = 16    # Начальное значение коэффициента D
    TRADINGSESSION                  = 18    # Торговые сессии
    TYPENAME                        = 9000  # Вид/категория ценной бумаги
    GROUP                           = 9001  # Код типа инструмента
    TYPE                            = 10000 # Тип бумаги
    GROUPNAME                       = 10011 # Типа инструмента
"""

class MoexMarketEnum(enum.IntEnum):
    SECID                           = 0     # Код индекса
    BOARDID                         = 1     # Идентификатор режима торгов
    BID                             = 2     # Лучшая котировка на покупку
    BIDDEPTH                        = 3     # Объем заявок на покупку по лучшей котировке, выраженный в лотах
    OFFER                           = 4     # Лучшая котировка на продажу
    OFFERDEPTH                      = 5     # Объём заявок на продажу по лучшей котировке, выраженный в лотах
    SPREAD                          = 6     #
    BIDDEPTHT                       = 7     # Объем всех заявок на покупку в очереди Торговой Системы, выраженный в лотах
    OFFERDEPTHT                     = 8     # Объём всех заявок на продажу в очереди Торговой Системы, выраженный в лотах
    OPEN                            = 9     # Цена первой сделки
    LOW                             = 10    # Минимальная цена сделки
    HIGH                            = 11    # Максимальная цена сделки
    LAST                            = 12    # Цена последней сделки
    LASTCHANGE                      = 13    #
    LASTCHANGEPRCNT                 = 14    #
    QTY                             = 15    # Объём последней сделки, в лотах
    VALUE                           = 16    # Объём последней сделки, в рублях
    VALUE_USD                       = 17    # Объём последней сделки, в долларах
    WAPRICE                         = 18    # Средневзвешенная цена
    LASTCNGTOLASTWAPRICE            = 19    #
    WAPTOPREVWAPRICEPRCNT           = 20    #
    WAPTOPREVWAPRICE                = 21    #
    CLOSEPRICE                      = 22    # Цена послеторгового периода
    MARKETPRICETODAY                = 23    # Рыночная цена по результатам торгов сегодняшнего дня, за одну ценную бумагу
    MARKETPRICE                     = 24    # Рыночная цена ценной бумаги по результатам торгов предыдущего дня, за одну ценную бумагу
    LASTTOPREVPRICE                 = 25    #
    NUMTRADES                       = 26    # Количество сделок за торговый день
    VOLTODAY                        = 27    # Объём совершенных сделок, выраженный в единицах ценных бумаг
    VALTODAY                        = 28    # Объём совершенных сделок, выраженный в рублях
    VALTODAY_USD                    = 29    # Объём совершенных сделок, выраженный в долларах
    ETFSETTLEPRICE                  = 30    #
    TRADINGSTATUS                   = 31    # Индикатор состояния торговой сессии по инструменту
    UPDATETIME                      = 32    #
    LASTBID                         = 33    # Лучшая котировка на покупку на момент завершения нормального периода торгов
    LASTOFFER                       = 34    # Лучшая котировка на продажу на момент завершения нормального периода торго
    LCLOSEPRICE                     = 35    # Официальная цена закрытия, рассчитываемая как средневзвешенная цена сделок последнего часа торговой сессии, включая сделки послеторгового периода
    LCURRENTPRICE                   = 36    # Официальная текущая цена, рассчитываемая как средневзвешенная цена сделок последнего, предшествующего моменту расчета, часа торговой сессии
    MARKETPRICE2                    = 37    # Рыночная цена 2, рассчитываемая в соответствии с методикой ФСФР
    NUMBIDS                         = 38    # Количество заявок на покупку в очереди Торговой системы
    NUMOFFERS                       = 39    # Количество заявок на продажу в очереди Торговой системы
    CHANGE                          = 40    # Изменение цены последней сделки по отношению к цене последней сделки предыдущего торгового
    TIME                            = 41    # Время заключения последней сделки
    HIGHBID                         = 42    # Наибольшая цена спроса в течение торговой сессии
    LOWOFFER                        = 43    # Наименьшая цена предложения в течение торговой сессии
    PRICEMINUSPREVWAPRICE           = 44    # Цена последней сделки к оценке предыдущего дня
    OPENPERIODPRICE                 = 45    # Цена предторгового периода
    SEQNUM                          = 46    #
    SYSTIME                         = 47    #
    CLOSINGAUCTIONPRICE             = 48    #
    CLOSINGAUCTIONVOLUME            = 49    #
    ISSUECAPITALIZATION             = 50    #
    ISSUECAPITALIZATION_UPDATETIME  = 51    #
    ETFSETTLECURRENCY               = 52    #
    VALTODAY_RUR                    = 53    #
    TRADINGSESSION                  = 54    #
    TRENDISSUECAPITALIZATION        = 55    #


def _get(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

class MoexAPI(_a.AbstractClient):
    _URL = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"

    def __init__(self, delay=1):
        super().__init__()
        self._updated = 0
        self._delay   = delay
        self._data    = None

    def update(self, force=False):
        if force or time.time()-self._updated >= self._delay:
            self._updated = time.time()
            self._data = _get(self._URL)

    def update_ticker(self, ticker : _a.AbstractInstrument):
        self.update()
        if self._data is not None:
            for data in self._data["marketdata"]["data"]:
                if data[0] == ticker.code:
                    return data
        return None


class MoexTicker(_a.AbstractInstrument):
    _URL = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{}/candles.json?interval={}&from={}"

    def __init__(self, api, ticker_code):
        super().__init__(ticker_code)
        self._api  = api

    def update(self):
        data = self._api.update_ticker(self)

        date        = data[MoexMarketEnum.TIME]
        open_price  = data[MoexMarketEnum.OPEN]                 or 0
        close_price = data[MoexMarketEnum.CLOSEPRICE]           or 0
        high        = data[MoexMarketEnum.HIGH]                 or 0
        low         = data[MoexMarketEnum.LOW]                  or 0
        volume      = data[MoexMarketEnum.CLOSINGAUCTIONVOLUME] or 0
        self._chart.attach(date, open_price, close_price, high, low, volume)

    def candles(self, interval, date, set_to_chart=False):                              # !!! Этому тут не место?
        """
        :param interval: 1, 10, – минут, 24 - день
        :param date: дата, например, "2025-03-11"
        :return:
        """
        data = _get(self._URL.format(self.code, interval, date))

        dates   = []
        opens   = []
        closes  = []
        highs   = []
        lows    = []
        volumes = []
        for obj in data["candles"]["data"]:
            opens   += [obj[0]]
            closes  += [obj[1]]
            highs   += [obj[2]]
            lows    += [obj[3]]
            volumes += [obj[5]]
            dates   += [obj[6].split(' ')[1]]

        self._chart.clear()
        self._chart.load(dates, opens, closes, highs, lows, volumes)

