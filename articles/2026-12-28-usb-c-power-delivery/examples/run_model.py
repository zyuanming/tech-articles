"""把 pd.py 的结果写成 results.json。"""

import json
import pathlib

import pd

HERE = pathlib.Path(__file__).resolve().parent


def main():
    data = pd.build()
    (HERE / 'results.json').write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    print('results.json', (HERE / 'results.json').stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
