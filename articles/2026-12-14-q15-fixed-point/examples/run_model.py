"""跑一遍 q15 模型，写 results.json。只做这一件事。"""

import json
from pathlib import Path

import q15

HERE = Path(__file__).resolve().parent


def main():
    R = q15.build()
    out = HERE / 'results.json'
    out.write_text(json.dumps(R, indent=1, ensure_ascii=False, sort_keys=False) + '\n')
    print('wrote', out)


if __name__ == '__main__':
    main()
