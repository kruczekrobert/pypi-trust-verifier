import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

github_login = input("Your github login: ")
github_password = input("Your github password: ")


def generate_report(verified, not_verified):
    with open('report.txt', 'a') as report_file:
        for v_data in verified:
            report_file.write("{}: {}\n".format(v_data, 'verified'))
        for nv_data in not_verified:
            report_file.write("{}: {}\n".format(nv_data, 'not verified'))


def is_top_downloaded(package_name):
    r = requests.get('https://hugovk.github.io/top-pypi-packages/top-pypi-packages-365-days.json')
    if package_name.lower() in str(r.content.lower()):
        return True
    return False


def format_package_name(name):
    return name[:name.index('==')]


def search_repository_path(req):
    soup = BeautifulSoup(req.content, 'lxml')
    github_repository_divs = soup.find_all("div", {"class": "github-repo-info"})
    try:
        first_elem_with_data_url = github_repository_divs[0].get('data-url')
        if first_elem_with_data_url:
            return first_elem_with_data_url
    except IndexError:
        return None


def is_verified(req):
    api_content = json.loads(req.content)
    last_update = api_content['updated_at']
    stars = api_content['stargazers_count']
    last_update_date_format = datetime.strptime(last_update[:10], "%Y-%m-%d")

    if last_update_date_format.year <= 2017 or stars < 200:
        return False
    return True


def verify_requirements_file():
    verified_list = []
    not_verified_list = []
    with open('requirements.txt', 'r') as requirements_file:
        for package in requirements_file:
            _package = format_package_name(package)
            print('Checking {}...'.format(_package))
            api_link = search_repository_path(
                req=requests.get('https://pypi.org/project/{}/'.format(_package))
            )
            if api_link is not None:
                api_req = requests.get(api_link)
                verified_list.append(_package) if is_verified(api_req) else not_verified_list.append(_package)
            else:
                verified_list.append(_package) if is_top_downloaded(_package) else not_verified_list.append(_package)
    generate_report(verified_list, not_verified_list)


verify_requirements_file()
