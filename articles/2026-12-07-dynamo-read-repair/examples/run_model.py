"""跑模型，写 results.json。只调 dynamo.build()。"""

import json
import os

import dynamo


def main():
    result = dynamo.build()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json')
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False, sort_keys=False)
    print('wrote %s' % path)


if __name__ == '__main__':
    main()
