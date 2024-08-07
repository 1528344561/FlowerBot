import random
import time
import json
import requests
from plugins.FlowerCore.configs import *


def link(problem):
    try:
        return "https://codeforces.com/problemset/problem/" + str(problem['contestId']) + '/' + str(
            problem['index'])
    # except KeyError:
    except Exception as e:
        return str(problem)


def get_recent_submission(CF_id):
    if not CF_id:
        return '请先绑定账号'
    try:
        json = requests.get('https://codeforces.com/api/user.status?handle={:s}&from=1&count=1'.format(CF_id)).json()
        # json = requests.get('https://codeforc.es/api/user.status?handle={:s}&from=1&count=1'.format(CF_id)).json()
        print(json)
        if json['status'] == 'FAILED':
            return None
        try:
            return json['result'][0]
        except IndexError:
            return None
    except requests.exceptions.JSONDecodeError:
        return None


def problem_name(problem, rating=False):
    try:
        if rating:
            return str(problem['contestId']) + str(problem['index']) + '(*{:d})'.format(problem['rating'])
        return str(problem['contestId']) + str(problem['index'])
    except KeyError:
        return str(problem)


problems = []


def fetch_problems() -> bool:
    global problems
    # cookies={
    #     '39ce7':'CFS3dMfB',
    #     "JSESSIONID":'F78C406FFAEE17367C818CEE7363C416',
    #     "cf_clearance":"uhy.KAFzUqdYLpK0IDtDSGknBCFEHCF2YJN9B9e2NjE-1717167284-1.0.1.1-Y2fvzaDYVBU0DIsrHcWYcBw_H.tkqomwxbtnX8ozFSTj2KyJsRlsGrlGlEioynL1oWiuAwjQTKdNunBmTUsBMA"
    # }
    for cnt in range(10):
        try:
            header={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36'}
            problems = (requests.get('https://codeforces.com/api/problemset.problems',headers=header).json())['result']['problems']
            
            # problems = (requests.get('https://codeforc.es/api/problemset.problems',headers=header).json())['result']['problems']
            return True
        except Exception as e:
            print(e)
            pass
    with open('./cf.txt','r',encoding='utf-8')as fp:
        txt = fp.read()
    problems = json.loads(txt)['result']['problems']
    return True


def daily_problem():
    t = time.localtime(time.time())
    res = []
    for x in problems:
        try:
            if x['rating'] <= DAILY_UPPER_BOUND and '*special' not in x['tags']:
                res.append(x)
        except KeyError:
            pass
    seed = (t.tm_year * 10000 + t.tm_mon * 33 * t.tm_mday) % len(res)
    print(res[seed]['tags'])
    return res[seed]


def problem_record(user):
    try:
        try:
            d = requests.get('https://codeforces.com/api/user.status?handle=' + user, timeout=5)
            # d = requests.get('https://codeforc.es/api/user.status?handle=' + user, timeout=5)
        except TimeoutError:
            return set()
        JSON = d.json()
        if JSON['status'] != 'OK':
            return []
        res = {problem_name(x["problem"]) for x in JSON['result']}
        return res
    except:
        return set()


def request_problem(tags, excluded_problems=None):
    if excluded_problems is None:
        excluded_problems = set()
    assert (type(tags[0]) == int)
    rating = tags[0]
    tags = tags[1:]
    result = []
    for x in problems:
        if (not 'tags' in x) or (not 'rating' in x) or (not 'contestId' in x):
            continue
        if excluded_problems is not None:
            if problem_name(x) in excluded_problems:
                continue
        flag = 1
        for y in tags:
            if y == 'not-seen':
                continue
            if y[0] != '!':
                if y == 'new':
                    if 'contestId' in x and x['contestId'] < NEW_THRESHOLD:
                        flag = 0
                    continue
                if not y in x['tags']:
                    flag = 0
            else:
                if y == '!new':
                    if 'contestId' in x and x['contestId'] >= NEW_THRESHOLD:
                        flag = 0
                    continue
                if y[1:] in x['tags']:
                    flag = 0
        if '*special' in x['tags'] and '!*special_problem' not in tags:
            flag = 0
        if not flag:
            continue
        if x['rating'] == rating:
            result.append(x)
    if not result:
        return None
    return random.choice(result)
