import pandas as pd
import numpy as np
import helper_funcs as hf
from collections import OrderedDict
from collections import defaultdict

def ordered_dict(column, k):
    d = column.value_counts()[:k].to_dict()
    return OrderedDict(sorted(d.items(), key=lambda x: x[1], reverse=True))

def tryConvert(cell):
    """
    convert a cell, if possible, to its supposed type(int, float, string)
    note: type of NaN cell is float
    """
    try:
        return int(cell)
    except ValueError, TypeError:
        try:
            return float(cell)
        except ValueError, TypeError:
            return cell

def numerical_stats(column,num_nonblank,sigma=3):
    """
    calculates numerical statistics
    """
    stats = column.describe()
    idict = {}
    idict["mean"] = stats["mean"]
    idict["standard-deviation"] = stats["std"]
    idict["Q1"] = stats["25%"]
    idict["Q2"] = stats["50%"]
    idict["Q3"] = stats["75%"]
    idict["count"] = int(stats["count"])
    idict["ratio"] = stats["count"]/num_nonblank
    outlier = column[(np.abs(column-stats["mean"])>(3*stats["std"]))]
    # shall we return outlier values?
    idict["num_outlier"] = outlier.count()
    return idict

def compute_numerics(column, feature):
    """
    computes numerical features of the column:
    # of integers/ decimal(float only)/ nonblank values in the column
    statistics of int/decimal/numerics
    """
    convert = lambda v: tryConvert(v)
    col = column.apply(convert)
    #col = pd.to_numeric(column,errors='ignore') #doesn't work in messy column?

    col_nonblank = col.dropna()
    col_int = pd.Series([e for e in col_nonblank if type(e) == int or type(e) == np.int64])
    col_float = pd.Series([e for e in col_nonblank if type(e) == float or type(e) == np.float64])

    feature["num_nonblank"] = col_nonblank.count()

    if col_int.count() > 0:
        feature["numeric_stats"]["integer"] = numerical_stats(col_int,feature["num_nonblank"])

    if col_float.count() > 0:
        feature["numeric_stats"]["decimal"] = numerical_stats(col_float,feature["num_nonblank"])

    if "integer" in feature or "decimal" in feature:
        feature["numeric_stats"]["numeric"] = numerical_stats(pd.concat([col_float,col_int]),feature["num_nonblank"])

def compute_common_numeric_tokens(column, feature, k=10):
    """
    compute top k frequent numerical tokens and their counts.
    tokens are integer or floats
    e.g. "123", "12.3"
    """
    #num_split = lambda x: filter(lambda y: unicode(y).isnumeric(),x.split())    
    num_split = lambda x: filter(lambda y: hf.is_Decimal_Number(y), x.split())
    token = column.dropna()
    if not token.empty:
        token = token.apply(num_split).apply(pd.Series).unstack().dropna()
    #token = column.fillna("_").apply(num_split).apply(pd.Series).unstack().dropna()
        if token.count() > 0:
            #if ("frequent-entries" not in feature.keys()):
            #    feature["frequent-entries"] = {}
            feature["frequent-entries"]["most_common_numeric_tokens"] = ordered_dict(token, k)

def compute_common_alphanumeric_tokens(column, feature, k=10):
    """
    compute top k frequent alphanumerical tokens and their counts.
    tokens only contain alphabets and/or numbers, decimals with points not included 
    """
    alnum_split = lambda x: filter(lambda y: y.isalnum(),x.split())
    token = column.dropna()
    if not token.empty:
        token = token.apply(alnum_split).apply(pd.Series).unstack().dropna()
    #token = column.fillna("_").apply(alnum_split).apply(pd.Series).unstack().dropna()
        if token.count() > 0:
            #if ("frequent-entries" not in feature.keys()):
            #    feature["frequent-entries"] = {}
            feature["frequent-entries"]["most_common_alphanumeric_tokens"] = ordered_dict(token, k)

def compute_common_values(column, feature, k=10):
    """
    compute top k frequent cell values and their counts.
    """
    if column.count() > 0:
        if ("frequent-entries" not in feature.keys()):
            feature["frequent-entries"] = {}
        feature["frequent-entries"]["most_common_values"] = ordered_dict(column, k)

def compute_common_tokens(column, feature, k=10):
    """
    compute top k frequent tokens and their counts.
    currently: tokens separated by white space
    at the same time, count on tokens which contain number(s)
    e.g. "$100", "60F", "123-456-7890"
    note: delimiter = " "
    """
    token = column.dropna()
    if not token.empty:
        #token = token.apply(lambda x: x.split()).apply(pd.Series).unstack()
        token = token.str.split(expand=True).unstack()
        contain_digits = lambda x: any(char.isdigit() for char in x)
        token_cnt = token.count()
        if token_cnt > 0:
            #if ("frequent-entries" not in feature.keys()):
            #    feature["frequent-entries"] = {}
            feature["frequent-entries"]["most_common_tokens"] = ordered_dict(token, k)
            cnt = token.dropna().apply(contain_digits).sum()
            feature["numeric_stats"]["contain_numeric_token"] = {}
            feature["numeric_stats"]["contain_numeric_token"]["count"] = cnt
            feature["numeric_stats"]["contain_numeric_token"]["ratio"] = float(cnt)/token_cnt

def compute_common_tokens_by_puncs(column, feature, k=10):
    """
    tokens seperated by all string.punctuation characters:
    '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
    """
    alnum_split = lambda x: "".join((word if word.isalnum() else " ") for word in x).split()
    token = column.dropna()
    if not token.empty:
        token = token.apply(alnum_split).apply(pd.Series).unstack()
        token_cnt = token.count()
        if token_cnt > 0:
            #if ("frequent-entries" not in feature.keys()):
            #    feature["frequent-entries"] = {}
            feature["frequent-entries"]["most_common_tokens_puncs"] = ordered_dict(token, k)
            #feature["num_tokens_puncs"] = token_cnt
            feature["distinct"]["num_distinct_tokens_puncs"] = token.nunique()
    #something else?

def compute_numeric_density(column, feature):
    """
    compute overall density of numeric characters in the column.
    """
    density = lambda x: (sum(c.isdigit() for c in x),len(x))
    column = column.dropna()
    if not column.empty:
        digit_total = column.apply(density).apply(pd.Series).sum()
        feature["numeric_stats"]["numeric_density"] = float(digit_total[0])/digit_total[1]

def compute_contain_numeric_values(column, feature):
    """
    caculate # and ratio of cells in the column which contains numbers. 
    """
    contain_digits = lambda x: any(char.isdigit() for char in x)
    cnt = column.dropna().apply(contain_digits).sum()
    if cnt > 0:
        feature["numeric_stats"]["contain_numeric"] = {}
        feature["numeric_stats"]["contain_numeric"]["count"] = cnt
        feature["numeric_stats"]["contain_numeric"]["ratio"] = float(cnt)/column.count()

