import requests

username = 'pontus'
password = 'pontus'
cookies = None


def login():
    global username
    global password

    response = requests.post(
        'https://m.lophoctiengnhat.com/ajax/checkLogin.php',
        "tendangnhap=" + username + "&matkhau=" + password + "&p=1"
    )

    global cookies
    cookies = response.cookies


def http_get(url: str) -> str:
    global cookies

    if not cookies:
        login()

    response = requests.get(url, cookies=cookies)
    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return ''

    html = response.content.decode('utf-8')
    return html
