import requests
import os
import sys

def set_github_action_output(name, value):
    with open(os.path.abspath(os.environ['GITHUB_OUTPUT']), 'a') as f:
        f.write(f'{name}={value}\n')

def get_check_suite_url():
    if int(os.getenv('GITHUB_RUN_ATTEMPT')) > 1:
        attempt = int(os.getenv('GITHUB_RUN_ATTEMPT')) - 1
    else:
        attempt = 1

    url = f'https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/attempts/{attempt}'
    r = requests.get(url,
                     headers={
                         'Authorization': f'Bearer {os.getenv("INPUT_GITHUB_TOKEN")}',
                         'Accept': 'application/vnd.github+json',
                         'X-GitHub-Api-Version': '2022-11-28'
                     })
    set_github_action_output('check_suite_url', r.json()['check_suite_url'])
    return r.json()['check_suite_url']


def get_check_run_annotation_url(check_suite_url):
    r = requests.get(f'{check_suite_url}/check-runs',
                     headers={
                         'Authorization': f'Bearer {os.getenv("INPUT_GITHUB_TOKEN")}',
                         'Accept': 'application/vnd.github+json',
                         'X-GitHub-Api-Version': '2022-11-28'
                     })
    for check_run in r.json()['check_runs']:
        if check_run['name'] == os.getenv('INPUT_CHECK_NAME'):
            set_github_action_output('annotations_url', check_run['output']['annotations_url'])
            return check_run['output']['annotations_url']

def get_annotations(annotations_url):
    r = requests.get(annotations_url,
                     headers={
                         'Authorization': f'Bearer {os.getenv("INPUT_GITHUB_TOKEN")}',
                         'Accept': 'application/vnd.github+json',
                         'X-GitHub-Api-Version': '2022-11-28'
                     })
    return r.json()

get_check_run_annotation_url(get_check_suite_url())
