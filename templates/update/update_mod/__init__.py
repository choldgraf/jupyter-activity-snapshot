import requests
import pandas as pd
import numpy as np
import os
from datetime import timedelta
from ipywidgets import widgets
from IPython.display import display

comments_query = """\
        comments(last: 100) {
          edges {
            node {
              authorAssociation
              createdAt
              updatedAt
              url
              author {
                login
              }
            }
          }
        }
"""

base_elements = """\
        state
        id
        title
        url
        createdAt
        updatedAt
        closedAt
        number
        authorAssociation
        author {
          login
        }
"""

gql_template = """\
{{
  search({query}) {{
    issueCount
    pageInfo {{
        endCursor
        hasNextPage
    }}
    nodes {{
      ... on PullRequest {{
        {base_elements}
        mergedBy {{
          login
        }}
        {comments}
      }}
      ... on Issue {{
        {base_elements}
        {comments}
      }}
    }}
  }}
}}
"""




# Define our query object that we'll re-use for github search
class GitHubGraphQlQuery():
    def __init__(self, query, display_progress=True):
        self.query = query
        self.headers = {"Authorization": "Bearer %s" % os.environ['GITHUB_ACCESS_TOKEN']}
        self.gql_template = gql_template
        self.display_progress = display_progress

    def request(self, n_pages=100, n_per_page=50):
        self.raw_data = []
        for ii in range(n_pages):
            search_query = ["first: %s" % n_per_page, 'query: "%s"' % self.query, 'type: ISSUE']

            if ii != 0:
                search_query.append('after: "%s"' % pageInfo['endCursor'])

            this_query = self.gql_template.format(
                query=', '.join(search_query),
                comments=comments_query,
                base_elements=base_elements
            )
            request = requests.post('https://api.github.com/graphql', json={'query': this_query}, headers=self.headers)
            if request.status_code != 200:
                raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, this_query))
            if "errors" in request.json().keys():
                raise Exception("Query failed to run with error {}. {}".format(request.json()['errors'], this_query))
            self.request = request

            # Parse the response
            json = request.json()['data']['search']
            if ii == 0:
                n_pages = int(np.ceil(json['issueCount'] / n_per_page))
                print("Found {} items, which will take {} pages".format(json['issueCount'], n_pages))
                prog = widgets.IntProgress(
                    value=0,
                    min=0,
                    max=n_pages,
                    description='Downloading:',
                    bar_style='',
                )
                if n_pages > 1 and self.display_progress:
                    display(prog)
                    
            # Add the JSON to the raw data list
            self.raw_data.append(json)
            pageInfo = json['pageInfo']
            self.last_query = this_query
            
            # Update progress and should we stop?
            prog.value += 1
            if pageInfo['hasNextPage'] is False:
                prog.bar_style = 'success'
                break
        
        if self.raw_data[0]['issueCount'] == 0:
            print("Found no entries for query {}".format(self.query))
            self.data = None
            return
        
        # Add some extra fields
        self.data = pd.DataFrame([jj for ii in self.raw_data for jj in ii['nodes']])
        self.data['author'] = self.data['author'].map(lambda a: a['login'] if a is not None else a)
        self.data['org'] = self.data['url'].map(lambda a: a.split('/')[3])
        self.data['repo'] = self.data['url'].map(lambda a: a.split('/')[4])
        
def extract_comments(comments):
    """Extract the comments returned from GraphQL Issues or PullRequests"""
    list_of_comments = [ii['edges'] for ii in comments]
    has_comments = any(jj.get('node') for ii in list_of_comments for jj in ii)
    
    # If we have no comments, just return None
    if not has_comments:
        return None

    comments = [jj.get('node') for ii in list_of_comments for jj in ii]
    comments = pd.DataFrame(comments)
    comments['author'] = comments['author'].map(lambda a: a['login'] if a is not None else a)
    
    # Parse some data about the comments
    url_parts = [ii.split('/') for ii in comments['url'].values]
    url_parts = np.array([(ii[3], ii[4], ii[6]) for ii in url_parts])
    orgs, repos, url_parts = url_parts.T

    issue_id = [ii.split('#')[0] for ii in url_parts]
    comment_id = [ii.split('-')[-1] for ii in url_parts]

    # Assign new variables
    comments['org'] = orgs
    comments['repo'] = repos
    comments['issue_id'] = issue_id
    comments['id'] = comment_id
    return comments