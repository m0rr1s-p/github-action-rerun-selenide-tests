import requests
import os
import sys
import logging

headers = {
    'Authorization': f'Bearer {os.getenv("INPUT_GITHUB_TOKEN")}',
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def set_github_action_output(name, value):
    with open(os.path.abspath(os.environ['GITHUB_OUTPUT']), 'a') as f:
        f.write(f'{name}={value}\n')

def get_attempt_job_annotations_url():
    if int(os.getenv('GITHUB_RUN_ATTEMPT')) > 1:
        attempt = int(os.getenv('GITHUB_RUN_ATTEMPT')) - 2
        logging.info(f'Attempt: {attempt}')
    else:
        attempt = 1
        logging.info(f'Attempt: {attempt}')
        sys.stdout.write('::notice title=No previous attempt::This is the first attempt, no previous attempt to rerun.')
        sys.stdout.write(os.linesep)

    url = f'https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}/attempts/{attempt}/jobs'
    logging.info(f'Requesting URL: {url}')
    r = requests.get(url, headers=headers)

    print(os.getenv('INPUT_CHECK_NAME'))
    print(r.json())
    print(r.json()['jobs'])
    if any(d.get("name") == os.getenv('INPUT_CHECK_NAME') for d in r.json()['jobs']):
        logging.info(f'Job found: {os.getenv("INPUT_CHECK_NAME")}')
        for job in r.json()['jobs']:
            if job['name'] == os.getenv('INPUT_CHECK_NAME'):
                attempt_job_annotation_url = f'{job["check_run_url"]}/annotations'
                set_github_action_output('attempt_job_annotation_url', attempt_job_annotation_url)
                return attempt_job_annotation_url
    else:
        logging.info(f'Job not found: {os.getenv("INPUT_CHECK_NAME")}')
        sys.stdout.write('::notice title=No job found::No job found.')
        sys.stdout.write(os.linesep)
        sys.exit(0)

def get_annotations(annotations_url):
    logging.info(f'Requesting URL: {annotations_url}')
    r = requests.get(annotations_url, headers=headers)
    return r.json()

def create_maven_command(annotations):
    logging.info(f'Creating maven command from annotations.')
    maven_tests_list = []
    for annotation in annotations:
        test = annotation['path']
        method = annotation['title'].split(' ')[0]
        maven_tests_list.append(f'{test}#{method}')
        maven_tests_string = ','.join(maven_tests_list)
    maven_command = f'mvn -D.surefire.rerunFailingTestsCount=2 -Dsurefire.failIfNoSpecifiedTests=false -pl selenide -am -Dtest={maven_tests_string} test -e --settings settings.xml'
    set_github_action_output('maven_command', maven_command)
    logging.info(f'Maven command: {maven_command}')
    return maven_command



job_annotations = []
job_annotation_url = get_attempt_job_annotations_url()
if len(job_annotation_url) > 0:
    job_annotations = get_annotations(job_annotation_url)
if len(job_annotations) > 0:
    create_maven_command(job_annotations)
