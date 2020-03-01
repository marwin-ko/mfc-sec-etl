from datetime import datetime
from glob import glob
import os


def is_current_dir_correct(osx=False):
    sep = '/' if osx else '\\'
    curr_sub_dirs = list(map(lambda s: s.split(f'{sep}')[-1], glob(os.getcwd() + f'{sep}*')))
    return all(sub_dir in curr_sub_dirs for sub_dir in ('sourcedata', 'mfc_sec_etl', 'results'))


def update_dict_with_cashflow_vals(d, cols, vals):
    for k, v in zip(cols, vals):
        d[k].append(v)
    return d


def make_cashflow_colnames(s):
    label = '{}_cashflow_20XX'.format(s)
    return [label if i == 0 else label+'-{}'.format(i) for i in range(5)]


def get_fname_from_sourcedata(osx=False):
    nl = '\n'
    sep = '/' if osx else '\\'
    print(os.getcwd())
    dir = f'{sep}'.join(os.getcwd().split(f'{sep}')[:-1])
    fnames = sorted(glob(f'{dir}{sep}sourcedata{sep}*'))
    prompt = f'Enter desired file number: {nl}'
    assert len(fnames) != 0, f'{nl}WARNING: No files in sourcedata folder!!!!!!!!!!!{nl}'
    for i, fname in enumerate(fnames, 1):
        prompt += f'[{i}] ' + f'{sep}'.join(fname.split(f'{sep}')[-2:]) + f'{nl}'
    idx = int(input(prompt))
    return fnames[idx-1]


def get_save_path(fname, osx=False):
    sep = '/' if osx else '\\'
    sname = fname.split(f'{sep}')[-1].split('.')[0] + '__' + datetime.now().strftime('%Y_%m_%d') + '.csv'
    dir = f'{sep}'.join(os.getcwd().split(f'{sep}')[:-1])
    spath = dir + f'{sep}results{sep}' + sname

    if os.path.exists(spath):
        if '_copy' in spath:
            print('WARNING ' * 10)
            print(f'You are writing over file: {spath}')
            print('WARNING ' * 10)
        else:
            # if file exists, but no copy, then append _copy.csv to file
            spath = spath[:-4] + '_copy.csv'
    print(f'This file will save @ {spath}')
    print()
    return spath
