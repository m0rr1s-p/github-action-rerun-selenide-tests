import requests
import os

def set_github_action_output(name, value):
    with open(os.path.abspath(os.environ['GITHUB_OUTPUT']), 'a') as f:
        f.write(f'{name}={value}\n')

set_github_action_output("test",os.getenv('INPUT_TEST'))



