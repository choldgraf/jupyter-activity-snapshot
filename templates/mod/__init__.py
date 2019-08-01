import pandas as pd
import os.path as op
import os
from glob import glob

def load_data(path_data_root, github_orgs=None):
    # Load data from all the orgs that we've listed
    comments = []
    issues = []
    prs = []
    
    if github_orgs is None:
        github_orgs = [ii.split(os.sep)[-1] for ii in glob(op.join(path_data_root, '*'))]

    for org in github_orgs:
        path_data = op.join(path_data_root, org)
        if not op.isdir(path_data):
            print(f"No data for {org}")
            continue
        comments.append(pd.read_csv(op.join(path_data, 'comments.csv'), index_col=0))
        issues.append(pd.read_csv(op.join(path_data, 'issues.csv'), index_col=0))
        prs.append(pd.read_csv(op.join(path_data, 'prs.csv'), index_col=0))

    comments = pd.concat(comments)
    issues = pd.concat(issues)
    prs = pd.concat(prs)
    
    return comments, issues, prs


def alt_theme():
    return {
        'config': {
            'axisLeft': {
                'labelFontSize': 15,
            },
            'axisBottom': {
                'labelFontSize': 15,
            },
        }
    }