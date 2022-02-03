# ========================================================================
# Copyright 2021 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================

__author__ = 'Jinho D. Choi'

import glob
import json
import os.path
from typing import Dict


def print_states(root: 'str'):
    years = sorted([os.path.basename(f) for f in glob.glob(os.path.join(root, '*'))])
    stats = {}
    for i, year in enumerate(years):
        for filename in glob.glob(os.path.join(root, year, '*.json')):
            d = json.load(open(filename))
            category = stats.setdefault(d['category'], [0]*len(years))
            category[i] += 1

    total = [0] * len(years)
    print('| Category | 2019 | 2020 | 2021 | Total |')
    print('|:--------:|-----:|-----:|-----:|------:|')
    for category, counts in sorted(list(stats.items())):
        for i in range(len(total)): total[i] += counts[i]
        print('| {} | {} | {} | {} | {} |'.format(category, counts[0], counts[1], counts[2], sum(counts)))
    print('| {} | {} | {} | {} | {} |'.format('Total', total[0], total[1], total[2], sum(total)))


if __name__ == '__main__':
    print_states('reviews')
