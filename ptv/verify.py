import sys
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup


def verify_in_top100(package_name):
    r = requests.get('https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.json')
    if package_name.lower() in str(r.content.lower()):
        return True
    return False


def format_package_name(name):
    return name[:name.index('==')]


def get_api_link(req):
    soup = BeautifulSoup(req.content, 'lxml')
    git_repo_divs = soup.findAll("div", {"class": "github-repo-info"})
    try:
        first_elem_with_data_url = git_repo_divs[0].get('data-url')
        if first_elem_with_data_url:
            return first_elem_with_data_url
    except IndexError:
        print('No github data for this package')
        return None


def verify_from_api(req, y, s, w):
    api_data = json.loads(req.content)
    last_update = api_data['updated_at']
    last_update_date = datetime.strptime(last_update[:10], "%Y-%m-%d")
    stars = api_data['stargazers_count']
    watchers = api_data['watchers_count']

    if (last_update_date.year <= y) or (stars <= s) or (watchers <= w):
        print(last_update_date.year, stars, watchers)
        return False
    else:
        print(last_update_date.year, stars, watchers)
        return True


# verify.py run <github-username> <password> <less than year> <less than stars> <less than watchers>
if sys.argv[1] == "run":
    verified_count = 0
    not_verified = []
    verified = []
    with open('requirements.txt', 'r') as f:
        package_list = f.readlines()
        for i, package in enumerate(package_list):
            f_package = format_package_name(package)
            api_link = get_api_link(
                req=requests.get('https://pypi.org/project/{}/'.format(f_package)))
            if api_link is not None:
                if verify_from_api(req=requests.get(api_link, auth=(sys.argv[2], sys.argv[3])), y=int(sys.argv[4]), s=int(sys.argv[5]), w=int(sys.argv[6])):
                    verified_count += 1
                    verified.append(f_package)
                    print(i, f_package, "Verified from GitHub")
                else:
                    not_verified.append(f_package)
                    print(i, f_package, "X")
            else:
                if verify_in_top100(f_package):
                    verified_count += 1
                    verified.append(f_package)
                    print(i, f_package, "but Verified from top 100")
                else:
                    not_verified.append(f_package)
                    print(i, f_package, "X")

    print(f'Verified: {len(verified)}, Not Verified: {len(not_verified)}, All: {len(package_list)}')
    print("Verified", verified)
    print("Not verified", not_verified)
