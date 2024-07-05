
import os


def load_string(file: str):
    with open(file=file, mode="r", encoding="utf-8") as f:
        s = f.read()
        f.close()
    return s


def dump_string(string: str, file: str, append: bool = False):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    mode = "w"
    if append:
        mode = "a"
    with open(file=file, mode=mode, encoding="utf-8") as f:
        f.write(string)
        f.close()


def load_dict(file: str):
    from json import loads
    return loads(load_string(file))


def dump_dict(d: dict, file: str, **kwargs):
    _kwargs = dict(indent=4, sort_keys=False)
    if len(kwargs.keys()) > 0:
        _kwargs.update(kwargs)
    from json import dumps
    return dump_string(dumps(d, **_kwargs), file)


def dump_tsv(
    df,
    table_file: str,
    col_names: list = None,
    reset_index: bool = False
):
    table_file = os.path.abspath(table_file)
    from pandas import DataFrame
    assert isinstance(df, DataFrame)
    _df = df.copy()
    os.makedirs(os.path.dirname(table_file), exist_ok=True)
    if col_names is not None and len(col_names) > 0:
        _df = _df.loc[:, col_names]
    if reset_index:
        _df.reset_index(inplace=True)
    _df.to_csv(table_file, encoding="utf-8", sep="\t", index=False, header=True)


def sanitize_float(s: str):
    from re import sub
    return float(sub("[^0-9\.]+", "", sub(",", ".", s)))


def randomize_sleep(min_: int = 1, max_: int = 5):
    from time import sleep
    from random import randint
    sleep(randint(min_, max_))


def hover_and_click(driver, element):
    from selenium.webdriver.common.action_chains import ActionChains
    ActionChains(driver).move_to_element(element).perform()
    randomize_sleep(1)
    driver.execute_script("arguments[0].click();", element)


def scroll_upon(driver, element):
    driver.execute_script("arguments[0].scrollIntoView();", element)
    randomize_sleep(1)


def remove_empty_values(input_list):
    output_list = []
    if input_list is not None:
        for i in input_list:
            if i is not None:
                try:
                    if len(i) > 0:
                        output_list.append(i)
                except TypeError:
                    continue
    return output_list
