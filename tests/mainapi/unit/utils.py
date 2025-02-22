# Кастомная либа для тестирования API
# Да, мне проще и быстрее написать либу,
# чем мучиться с готовыми решениями

import requests
from colorama import just_fix_windows_console
just_fix_windows_console()
from colorama import init
init()
from colorama import Fore, Back, Style
import json
import time
import uuid

testnum = 0
errorsnum = 0
servererrorsnum = 0
lastbody = None
log_info = True

METHOD_POST = "POST"
METHOD_GET = "GET"
METHOD_PUT = "PUT"
METHOD_DELETE = "DELETE"

times = []

def disable_logger_info(v):
    global log_info
    log_info = not v

def avg(arr):
    return sum(arr) / len(arr)

# Валидация ответа рекурсией
def validate_json(good, check, check_ord=True):
    # чек типов
    if not (type(good) == int and type(check) == float):
        if type(good) != type(check):
            return f"type missmatch (good: {type(good)} check: {type(check)})"
    # чек если словарь
    if type(good) == dict:
        for i in good.keys():
            if i not in check.keys():
                return f"key not found '{i}'"
            val = validate_json(good[i], check[i])
            if val != True:
                return f"[{i}] -> {val}"
    # чек если список
    if type(good) == list:
        # чекнем длину
        if len(good) != len(check):
            return f"list length not equal (good: {len(good)} check: {len(check)})"
        if check_ord:
            # если нужно чекать подядок элементов в списках
            for i in range(len(good)):
                val = validate_json(good[i], check[i])
                if val != True:
                    return f"[{i}] -> {val}"
        else:
            # если не нужно чекать порядок в списках
            for i in range(len(good)):
                gotval = False
                for j in range(len(check)):
                    val = validate_json(good[i], check[j])
                    if val == True:
                        gotval = True
                if not gotval:
                    return f"[any] -> no match"
    # чек если то, что можно валидировать ==
    if type(good) in [str, float, int]:
        if good != check:
            return "values not equal"
    # всё окей, нигде не споткнулись
    return True

def test(method, url, testname="", query_params={}, body=None, expected_body=None, expected_code=200, valid_check_order=True):
    global testnum, errorsnum, servererrorsnum, lastbody, log_info
    testnum += 1
    header = f"===== TEST #{testnum}{ ':' if testname != '' else '' } {testname}{ ' ' if testname != '' else '' }====="
    if log_info: print(Fore.BLUE + "=" * len(header) + Style.RESET_ALL)
    print(Fore.BLUE + header + Style.RESET_ALL)
    if log_info: print(Fore.BLUE + "=" * len(header) + Style.RESET_ALL)

    if method == METHOD_GET:
        req_fn = requests.get
    elif method == METHOD_POST:
        req_fn = requests.post
    elif method == METHOD_PUT:
        req_fn = requests.put
    elif method == METHOD_DELETE:
        req_fn = requests.delete
    else:
        raise Exception("Not valid method!")
    
    requestbody = json.dumps(body, ensure_ascii=False)

    print(f"[{method}] {url}")
    if log_info: print(f"Request body: {body}")

    starttime = time.time()
    try:
        r = req_fn(url, params=query_params, data=requestbody)
    except requests.exceptions.ConnectionError:
        print(Fore.RED + f"NOT PASSED: TIMEOUT!")
        print()
        errorsnum += 1
        return False
    endtime = time.time()

    timepassed = endtime - starttime

    if str(r.status_code)[0] == "5":
        servererrorsnum += 1
        print(Fore.RED + "Server error!" + Style.RESET_ALL)

    return_body = r.text
    try:
        return_body = r.json()
    except Exception as e:
        if log_info: print(Fore.YELLOW + "Return body not JSON!" + Style.RESET_ALL)
    lastbody = return_body

    if r.status_code != expected_code:
        print(Fore.RED + f"NOT PASSED: Unexpected return code! Code: {r.status_code}" + Style.RESET_ALL)
        print(f"Return code: {r.status_code}\nExpected code: {expected_code}")
        print(f"Return body: {return_body}\nExpected body: {expected_body}")
        print(f"Req time: {round(timepassed * 1000)} ms")
        print()
        errorsnum += 1
        return False
    
    if expected_body != None:
        val = validate_json(expected_body, return_body, valid_check_order)
        if val != True:
            print(Fore.RED + f"NOT PASSED: Unexpected return body!" + Style.RESET_ALL)
            print(f"Validation: {val}")
            print(f"Return code: {r.status_code}\nExpected code: {expected_code}")
            print(f"Return body: {return_body}\nExpected body: {expected_body}")
            print(f"Req time: {round(timepassed * 1000)} ms")
            print()
            errorsnum += 1
            return False
        
    if log_info:
        print(f"Return code: {r.status_code}\nExpected code: {expected_code}")
        print(f"Return body: {return_body}\nExpected body: {expected_body}")
    
    print(Fore.GREEN + f"PASSED" + Style.RESET_ALL)
    if log_info: print(f"Req time: {round(timepassed * 1000)} ms")
    print()
    times.append(timepassed)
    return True

def get_random_uuid():
    return str(uuid.uuid4())

def get_last_return_body():
    return lastbody

def summary():
    print()
    if errorsnum == 0:
        print(Fore.GREEN + "ALL PASSED!" + Style.RESET_ALL)
        print(f"Passed: {testnum - errorsnum}/{testnum}\nErrors: {errorsnum}")
    else:
        print(Fore.RED + "HAVE ERRORS!" + Style.RESET_ALL)
        print(f"Passed: {testnum - errorsnum}/{testnum}\nErrors: {errorsnum}")
        if servererrorsnum > 0:
            print(Fore.RED + f"Server errors: {servererrorsnum}" + Style.RESET_ALL)
    print(f"Response time: AVG={round(avg(times) * 1000)}ms MAX={round(max(times) * 1000)}ms MIN={round(min(times) * 1000)}ms")