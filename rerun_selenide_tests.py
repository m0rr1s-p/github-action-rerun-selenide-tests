import requests
import os
import sys

headers = {
    'Authorization': f'Bearer {os.getenv("INPUT_GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

annotations = []

def set_github_action_output(name, value):
    with open(os.path.abspath(os.environ['GITHUB_OUTPUT']), 'a') as f:
        f.write(f'{name}={value}\n')

def get_check_suite_url():
    if int(os.getenv('GITHUB_RUN_ATTEMPT')) > 1:
        attempt = int(os.getenv('GITHUB_RUN_ATTEMPT')) - 1
    else:
        attempt = 1
        sys.stdout.write('::notice title=No previous attempt::This is the first attempt, no previous attempt to rerun.')
        sys.stdout.write(os.linesep)

    url = f'https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/attempts/{attempt}'
    r = requests.get(url, headers=headers)
    set_github_action_output('check_suite_url', r.json()['check_suite_url'])
    return r.json()['check_suite_url']


def get_check_run_annotation_url(check_suite_url):
    r = requests.get(f'{check_suite_url}/check-runs', headers=headers)
    if any(d.get("name") == os.getenv('INPUT_CHECK_NAME') for d in r.json()['check_runs']):
        for check_run in r.json()['check_runs']:
            if check_run['name'] == os.getenv('INPUT_CHECK_NAME'):
                set_github_action_output('annotations_url', check_run['output']['annotations_url'])
                return check_run['output']['annotations_url']
    else:
        sys.stdout.write('::notice title=No check run found::No check run found.')
        sys.stdout.write(os.linesep)
        return None

def get_annotations(annotations_url):
    r = requests.get(annotations_url, headers=headers)
    return r.json()

def create_maven_command(annotations):
    maven_tests_list = []
    for annotation in annotations:
        test = annotation['path']
        method = annotation['title'].split(' ')[0]
        maven_tests_list.append(f'{test}#{method}')
        maven_tests_string = ','.join(maven_tests_list)
    maven_command = f'mvn -D.surefire.rerunFailingTestsCount=2 -Dsurefire.failIfNoSpecifiedTests=false -pl selenide -am -Dtest={maven_tests_string} test -e --settings settings.xml'
    set_github_action_output('maven_command', maven_command)
    print(maven_command)
    return maven_command


check_suite_url = get_check_suite_url()
if check_suite_url:
    annotation_url = get_check_run_annotation_url(check_suite_url)
if annotation_url:
    annotations = get_annotations(annotation_url)
if len(annotations) > 0:
    create_maven_command(annotations)