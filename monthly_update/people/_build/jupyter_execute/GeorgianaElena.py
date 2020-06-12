# Report for GeorgianaElena

import seaborn as sns
import pandas as pd
import numpy as np
import altair as alt
from markdown import markdown
from IPython.display import Markdown
from ipywidgets.widgets import HTML, Tab
from ipywidgets import widgets
from datetime import timedelta
from matplotlib import pyplot as plt
import os.path as op

from mycode import alt_theme
from warnings import simplefilter
simplefilter('ignore')

def author_url(author):
    return f"https://github.com/{author}"

# Parameters
fmt_date = "{:%Y-%m-%d}"

n_days = 30 * 2
start_date = fmt_date.format(pd.datetime.today() - timedelta(days=n_days))
end_date = fmt_date.format(pd.datetime.today())

renderer = "html"
person = "jasongrout"

# Parameters
person = "GeorgianaElena"
n_days = 60


alt.renderers.enable(renderer);
alt.themes.register('my_theme', alt_theme)
alt.themes.enable("my_theme")

## Load data

from pathlib import Path
path_data = Path("./")
comments = pd.read_csv(path_data.joinpath('comments.csv'), index_col=0)
issues = pd.read_csv(path_data.joinpath('issues.csv'), index_col=0)
prs = pd.read_csv(path_data.joinpath('prs.csv'), index_col=0)

comments = comments.query('author == @person').drop_duplicates()
issues = issues.query('author == @person').drop_duplicates()
closed_by = prs.query('mergedBy == @person')
prs = prs.query('author == @person').drop_duplicates()

# Time columns
# Also drop dates outside of our range
time_columns = ['updatedAt', 'createdAt', 'closedAt']
for col in time_columns:
    for item in [comments, issues, prs, closed_by]:
        if col not in item.columns:
            continue
        dt = pd.to_datetime(item[col]).dt.tz_localize(None)
        item[col] = dt
        item.query("updatedAt < @end_date and updatedAt > @start_date", inplace=True)

# Repository summaries

summaries = []
for idata, name in [(issues, 'issues'), (prs, 'prs'), (comments, 'comments')]:
    idata = idata.groupby(["repo", "org"]).agg({'id': "count"}).reset_index().rename(columns={'id': 'count'})
    idata["kind"] = name
    summaries.append(idata)
summaries = pd.concat(summaries)

repo_summaries = summaries.groupby(["repo", "kind"]).agg({"count": "sum"}).reset_index()
org_summaries = summaries.groupby(["org", "kind"]).agg({"count": "sum"}).reset_index()

repo_summaries['logcount'] = np.log(repo_summaries["count"])

ch1 = alt.Chart(repo_summaries, width=600, title="Activity per repository").mark_bar().encode(
    x='repo',
    y='count',
    color='kind',
    tooltip="kind"
)

ch2 = alt.Chart(repo_summaries, width=600, title="Log activity per repository").mark_bar().encode(
    x='repo',
    y='logcount',
    color='kind',
    tooltip="kind"
)

ch1 | ch2

alt.Chart(org_summaries, width=600).mark_bar().encode(
    x='org',
    y='count',
    color='kind',
    tooltip="org"
)

# By repository over time

## Comments

comments_time = comments.groupby('repo').resample('W', on='createdAt').count()['author'].reset_index()
comments_time = comments_time.rename(columns={'author': 'count'})
comments_time_total = comments_time.groupby('createdAt').agg({"count": "sum"}).reset_index()
ch1 = alt.Chart(comments_time, width=600).mark_line().encode(
    x='createdAt',
    y='count',
    color='repo',
    tooltip="repo"
)

ch2 = alt.Chart(comments_time_total, width=600).mark_line(color="black").encode(
    x='createdAt',
    y='count',
)

ch1 + ch2

## PRs

prs_time = prs.groupby('repo').resample('W', on='createdAt').count()['author'].reset_index()
prs_time = prs_time.rename(columns={'author': 'count'})
prs_time_total = prs_time.groupby('createdAt').agg({"count": "sum"}).reset_index()

ch1 = alt.Chart(prs_time, width=600).mark_line().encode(
    x='createdAt',
    y='count',
    color='repo',
    tooltip="repo"
)

ch2 = alt.Chart(prs_time_total, width=600).mark_line(color="black").encode(
    x='createdAt',
    y='count',
)

ch1 + ch2

closed_by_time = closed_by.groupby('repo').resample('W', on='closedAt').count()['author'].reset_index()
closed_by_time = closed_by_time.rename(columns={'author': 'count'})

alt.Chart(closed_by_time, width=600).mark_line().encode(
    x='closedAt',
    y='count',
    color='repo',
    tooltip="repo"
)

# By type over time

prs_time = prs[['author', 'createdAt']].resample('W', on='createdAt').count()['author'].reset_index()
prs_time = prs_time.rename(columns={'author': 'prs'})
comments_time = comments[['author', 'createdAt']].resample('W', on='createdAt').count()['author'].reset_index()
comments_time = comments_time.rename(columns={'author': 'comments'})

total_time = pd.merge(prs_time, comments_time, on='createdAt', how='outer')
total_time = total_time.melt(id_vars='createdAt', var_name="kind", value_name="count")


alt.Chart(total_time, width=600).mark_line().encode(
    x='createdAt',
    y='count',
    color='kind'
)