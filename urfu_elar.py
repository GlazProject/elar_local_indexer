import requests
import feedparser
from time import mktime
from datetime import datetime


def get_all_works_by_author(author: str) -> dict[str, datetime]:
    """
    Возвращает список всех работ указанного автора.
    :param author: ФИО автора для поиска в электронной библиотеке.
    :return: словарь с ключами url а значениями - датами последнего изменения
    :except: ElarException - Если невозможно получить все работы
    """
    items = {}
    rpp = 20
    start = 1 - rpp
    total_results = rpp + 2

    while start + rpp < total_results:
        start += rpp
        url = _get_url(author, start, rpp)
        # print(f'REQUESTED: {url}')
        start, rpp, total_results = _collect_works(author, url, items)
    return items


def _get_url(author: str, start: int = 1, per_page: int = 20):
    return f'https://elar.urfu.ru/open-search/?start={start}&rpp={per_page}&format=atom&query="{author}"'


def _collect_works(author: str, url: str, links: dict[str, datetime]) -> (int, int, int):
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout as e:
        raise ElarException(str(e))
    if not response:
        raise ElarException(f"Can not get page from {url}")

    data = feedparser.parse(response.content)
    total_results = int(data.feed.opensearch_totalresults)
    rpp = int(data.feed.opensearch_itemsperpage)
    start = int(data.feed.opensearch_startindex)
    # print(f'RESPONSE: start = {start}, rpp = {rpp}, total results = {total_results}')

    for entry in data.entries:
        if author in [a.name for a in entry.authors]:
            links[entry.link] = datetime.fromtimestamp(mktime(entry.updated_parsed))
    return start, rpp, total_results


class ElarException(Exception):
    def __init__(self, msg=""):
        self.msg = msg
