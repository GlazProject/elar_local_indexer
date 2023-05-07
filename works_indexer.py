import csv
import os
from pathlib import Path
from datetime import datetime

import urfu_elar
import urfu_elar_works


def start_index_works(authors: list[str], output_path: Path,
                      in_one_file: bool = False, only_store: bool = False):
    """
    Производит индексацию работ для переданных авторов.
    :param authors: список ФИО авторов, для которых нужно проиндексировать работы.
    :param output_path: Папка, в которую нужно сохранять новые работы.
    :param in_one_file: Флаг, показывающий, что все новые работы должны записываться в один общий файл.
    :param only_store: Флаг, показывающий, что необходимо все существующие работы записать как просмотренные.
    """
    index_path = output_path / '.index'
    index_path = index_path.resolve()

    if not index_path.exists():
        os.makedirs(index_path)

    main_output_file = output_path / 'updates.txt'
    for author in authors:
        index_file = index_path / f'index_{author}.csv'
        output_file = output_path / f'{author}.txt' if not in_one_file else main_output_file
        _index_works_for_author(author, index_file, output_file, only_store)


def _index_works_for_author(author: str, index_file: Path, output_file: Path, only_store: bool):
    print(f'Начато индексирование для {author}')

    old_works = {}
    try:
        all_works = urfu_elar.get_all_works_by_author(author)
    except urfu_elar.ElarException:
        print(f'Индексирование для {author} прервано из-за ошибки. Оно будет проведено в следующий раз\n')
        return

    if not only_store and index_file.exists():
        with index_file.open('r', newline='\n', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            for row in reader:
                if len(row) == 0:
                    continue
                old_works[row[0]] = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')

        for work in all_works:
            if work in old_works and all_works[work] <= old_works[work]:
                continue
            _load_work(author, output_file, work)

    with index_file.open('w', newline='\n', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',')
        for work in all_works:
            writer.writerow([work, all_works[work]])

    print(f'Завершено индексирование для {author}\n')


def _load_work(author: str, output_file: Path, url: str):
    print(f'Обнаружена новая работа у {author}: {url}')
    work = urfu_elar_works.work_from_url(url)
    result = ''
    if output_file.stem != author:
        result += f'Новая работа от: "{author}"\n'
    result += f'Проиндексирована {datetime.now()}\n' \
              f'----------------\n'
    result += work.to_string()
    result += '-' * 20 + '\n\n\n'

    with output_file.open('a+', newline='\n', encoding='utf-8') as file:
        file.write(result)
