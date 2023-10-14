
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
    import pandas as pd
    assert isinstance(df, pd.DataFrame)
    _df = df.copy()
    os.makedirs(os.path.dirname(table_file), exist_ok=True)
    if col_names is not None and len(col_names) > 0:
        _df = _df.loc[:, col_names]
    if reset_index:
        _df.reset_index(inplace=True)
    _df.to_csv(table_file, encoding="utf-8", sep="\t", index=False, header=True)
