import requests
from lxml import html
from dataclasses import dataclass


@dataclass(frozen=True)
class Work:
    title: str
    bibliographic_description: str
    about: str
    authors: list[str]
    created: str
    publisher: str
    doi: str
    isbn: str
    language: str
    url: str
    document_url: str
    keywords: list[str]
    sources: list[str]

    def to_string(self) -> str:
        result = _add('Название', self.title) + \
                 _add_many('Авторы', self.authors) + \
                 _add('Дата публикации', self.created) + \
                 _add('Издатель', self.publisher) + \
                 _add('Язык', self.language) + \
                 _add('Библиографическое описание', self.bibliographic_description) + \
                 _add('Аннотация', self.about) + \
                 _add('URL', self.url) + \
                 _add('Ссылка на документ', self.document_url) + \
                 _add('DOI', self.doi) + \
                 _add('ISBN', self.isbn) + \
                 _add_many('Ключевые слова', self.keywords) + \
                 _add_many('Источники', self.sources)
        return result


def work_from_string(document: str) -> Work:
    """
    Позволяет получить объект заполненной научной работы по данным из текста.
    :param document: Текст в формате html, который содержит все необходимые данные в тегах meta.
    :return: Объект типа Work - заполненный экземпляр данных о научной работе
    """
    head = html.document_fromstring(document).head
    return Work(
        title=_try_get_one_attribute('DC.title', head),
        bibliographic_description=_try_get_one_attribute('DCTERMS.bibliographicCitation', head),
        about=_try_get_one_attribute('DCTERMS.abstract', head),
        authors=_try_get_list_of_attributes('DC.creator', head),
        created=_try_get_one_attribute('DCTERMS.issued', head),
        publisher=_try_get_one_attribute('DC.publisher', head),
        doi=_try_get_one_attribute('citation_doi', head),
        isbn=_try_get_one_attribute('citation_isbn', head),
        language=_try_get_one_attribute('DC.language', head),
        url=_try_get_one_attribute('citation_abstract_html_url', head),
        document_url=_try_get_one_attribute('citation_pdf_url', head),
        keywords=_try_get_one_attribute('citation_keywords', head).split('; '),
        sources=_try_get_list_of_attributes('citation_journal_title', head)
    )


def work_from_url(url: str) -> [Work, None]:
    """
    Позволяет получить объект научной работы по данным из url.
    :param url: URL страницы elar urfu с научной работой.
    :return: Объект типа Work - заполненный экземпляр данных о научной работе
    """
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.ReadTimeout as e:
        print(f'[ERROR] {e}')
        return None
    if not response:
        print(f'Can not get work from url {url}')
        return None

    return work_from_string(response.text)


def _try_get_one_attribute(name: str, head) -> [str, None]:
    value = head.xpath(f'meta[@name="{name}"]/@content')
    return value.pop() if len(value) > 0 else None


def _try_get_list_of_attributes(name: str, head) -> [list[str], None]:
    values = head.xpath(f'meta[@name="{name}"]/@content')
    return values if len(values) > 0 else None


def _add(name: str, value: [str, None]):
    return '' if value is None else f'{name}: {value}\n'


def _add_many(name: str, value: [list[str], None]):
    if value is None:
        return ''
    return f'{name}: ' + ('\n' + ' ' * (len(name) + 2)).join(value) + '\n'
