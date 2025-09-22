import requests
import os
import sys

def set_github_action_output(name, value):
    with open(os.path.abspath(os.environ['GITHUB_OUTPUT']), 'a') as f:
        f.write(f'{name}={value}\n')

set_github_action_output("test",os.getenv('INPUT_TEST'))

def get_check_suite_url():
    if os.getenv('GITHUB_RUN_ATTEMPT') > '1':
        # TODO: remove print url
        url = f'https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/attempts/{int(os.getenv('GITHUB_RUN_ATTEMPT')) - 1}'
        print(url)
        r = requests.get(url,
                         headers={
                             'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN")}',
                             'Accept': 'application/vnd.github+json',
                             'X-GitHub-Api-Version': '2022-11-28'
                         })
        # TODO: remove print json
        print(r.json())
        set_github_action_output(r.json()['check_suite_url'], os.getenv('INPUT_TEST'))
        return r.json()['check_suite_url']
    else:
        sys.stdout.write("::notice title=no_attempt_found::No attempt found")
        sys.stdout.write(os.linesep)

get_check_suite_url()
