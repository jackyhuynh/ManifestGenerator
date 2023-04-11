#!/usr/bin/env python

import os
import subprocess

"""
    exit code 2 is the application don't recognize the current operating system
"""

# The CHARTS hold the different chart
CHARTS = ["base", "istiod", "gateway"]

# Folder that we need to check
MANIFESTS_DIR = "manifests"
VALUES_DIR = "values"
"""
This function check if a folder is in the directory
"""


def check_exist(folder_, result_):
    print(f'The folder {folder_} is exist.' if result_ == 0 else f'The folder {folder_} is NOT exist.')


"""
    check_operating_system() is check what is the current operating system that we are using
    Return code:
        1: Current OS is Unix or Linux
        2: Current OS is Windows
        3: Current OS is Mac OS
"""


def check_operating_system():
    if os.name == 'posix':
        # print('Current OS is Unix or Linux')
        return 0
    elif os.name == 'nt':
        # print('Current OS is Windows')
        return 1
    elif os.name == 'mac':
        # print('Current OS is macOS')
        return 2
    else:
        print('Unknown operating system! Will not be able to support! EXIT NOW...')
        exit(2)


"""
Navigate backward to in the directory structure.
"""


def navigate_backward():
    os.chdir('..')


"""
This function will return the appropriate backslash base on operating system
"""


def signed_directory_creation():
    if check_operating_system() == 0 or check_operating_system() == 2:
        return '/'
    elif check_operating_system() == 1:
        return '\\'


"""
This function will check if the specific directory is existed:
"""


def check_or_create_a_directory(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    else:
        print(f"{directory} is existed")


"""
process_validation(process_name, val_code) validate the execution of a subprocess
"""


def process_validation(process_name, val_code):
    content = f'process {process_name} is'
    print(f'{content} successfully executed' if val_code == 0 else f'{content} NOT executed')


# The directory Signed
LASH = signed_directory_creation()
cwd = os.getcwd()
# print(f'Current directory is {os.getcwd()}')

# Check if helm is install on the machine
helm_result = subprocess.run(['helm', 'version'], shell=True, capture_output=True, text=True)

if helm_result.returncode == 1:
    print("Helm is not installed, you can follow the installation instructions for your operating system on the "
          "official Helm website: https://helm.sh/docs/intro/install/")
    exit(1)

# Validate if the manifest directory and values directory is existed
check_or_create_a_directory(f'{cwd}{LASH}{MANIFESTS_DIR}')
check_or_create_a_directory(f'{cwd}{LASH}{VALUES_DIR}')

# connect to the upstream Helm repository
process_validation('add repo to the upstream',
                   subprocess.run('helm repo add istio https://istio-release.storage.googleapis.com/charts', shell=True,
                                  capture_output=True, text=True).returncode)

process_validation('update helm repo',
                   subprocess.run('helm repo update', shell=True, capture_output=True, text=True).returncode)

# create the default value
check_or_create_a_directory(f'{cwd}{LASH}{VALUES_DIR}{LASH}default')

# create the content in default folder:
for chart in CHARTS:
    # print(chart)
    process_validation(f'creating {chart}', subprocess.run(
        ['helm', 'show', 'values', f'istio/{chart}', '>',
         f"{VALUES_DIR}{LASH}default{LASH}{chart}-default-values.yaml"],
        shell=True, capture_output=True, text=True).returncode)

for dir_ in os.listdir(f'{os.getcwd()}{LASH}{VALUES_DIR}'):

    # ignore the default manifest
    if dir_ == 'default':
        continue

    check_or_create_a_directory(f'{os.getcwd()}{LASH}{MANIFESTS_DIR}{LASH}{dir_}')
    # print(dir_)
    # print(f'current directory is {os.getcwd()}')

    for chart in CHARTS:

        print(f'[*] Generating ${MANIFESTS_DIR}/${dir_}/${chart}.yaml')

        print(f'{os.getcwd()}{LASH}{VALUES_DIR}{LASH}{dir_}{LASH}{chart}-values.yaml')

        unique_values = ''
        if os.path.exists(f'{os.getcwd()}{LASH}{VALUES_DIR}{LASH}{dir_}{LASH}{chart}-values.yaml'):
            unique_values = f"-f ${VALUES_DIR}{LASH}{dir}{LASH}{chart}-values.yaml"
            print(unique_values)

        extra_install_values = '--include-crds --create-namespace'
        name_space = 'istio-system'
        if chart == 'gateway':
            name_space = 'istio-gateway'
        elif chart == 'cni':
            name_space = 'kube-system'

        command = f'helm template istio istio/{chart} --namespace {name_space} {extra_install_values} {unique_values} > {MANIFESTS_DIR}{LASH}{dir_}{LASH}{chart}.yaml'
        print(command)
        process_validation(f'generate {chart} manifest',
                           subprocess.run(command, shell=True, capture_output=True, text=True).returncode)

"""
This version is to install the helm chart and pull it
"""

# # Use Subprocess to move to a real directory
# # Create the helm_chart directory
# subprocess.run(['mkdir', 'helmchart'], shell=True)
#
# # Change the current directory to helmchart
# os.chdir('helmchart')
#
# subprocess.Popen('git init', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# subprocess.Popen('git remote add -f origin https://github.com/kiali/helm-charts.git', shell=True)
# subprocess.Popen('git config core.sparseCheckout true', shell=True)
# subprocess.Popen('git sparse-checkout set "kiali-server"', shell=True)
# subprocess.Popen('git pull origin master', shell=True)
