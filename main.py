from pathlib import Path

import works_indexer
from argparse import ArgumentParser


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-a', '--authors', type=str, dest='authors',
                        help='Файл с записанными построчно именами авторов для индексации', required=True)
    parser.add_argument('-o', '--output_path', type=str, dest='output_path',
                        help='Путь к папке, в которую сохранять обновления для авторов', required=True)
    parser.add_argument('--all_works_are_old', action='store_true',
                        help='Если это первый запуск и необходимо запомнить уже загруженные работы, '
                             'то необходимо поднять данный флаг')
    parser.add_argument('--all_in_one_file', action='store_true',
                        help='Сохранять изменения обо всех авторах в один файл. По умолчанию каждому автору свой файл')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    with open(args.authors, 'r', encoding='utf-8') as file:
        authors = [a.strip() for a in file.readlines()]
    print(f'Прочитано авторов: {len(authors)}')
    works_indexer.start_index_works(authors, Path(args.output_path), args.all_in_one_file, args.all_works_are_old)
