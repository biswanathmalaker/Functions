import requests
from tqdm import tqdm
import os

def download_from_url(url,file_path):
    import requests
    import os
    try:
        if not os.path.isfile(file_path):
            r = requests.get(url,allow_redirects = True)
            f = open(file=file_path,mode='wb')
            f.write(r.content)
            f.close()
            return f'{file_path} downloaded'
        else:
            print(f"{file_path} exists!")
    except Exception as error:
        print(f"Error : {error} ---> {file_path}")
        return error



def get_all_urls(url):
    from bs4 import BeautifulSoup
    from urllib.request import Request, urlopen
    import re

    req = Request(url)
    html_page = urlopen(req)

    soup = BeautifulSoup(html_page, "lxml")

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    return links


def all_links_from_response(response):
    from bs4 import BeautifulSoup
    from urllib.request import Request, urlopen
    import re

    soup = BeautifulSoup(response.content, "lxml")

    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))

    return links




def session_download(file_urls,**kwargs):
    """
    Download files having a common path keeping connection maintained.
    kwargs---> either out_paths (list , having length same as file urls) (useful if one wants to change
                                    file names when downloading)
                or out_dir ("a string where all the files would be stored.) (
                                        files would be saved as same name as on internet.)
                pr -->(print download status? True or False)
    """
    import requests
    import os

    options = {
        "out_paths"     :   None,
        "out_dir"       :   None,
        "pr"            :   False
    }

    options.update(kwargs)

    out_paths   = options['out_paths']
    out_dir     = options['out_dir']
    pr          = options['pr']



    # Create a session for persistent connection
    session = requests.Session()
    if out_paths != None:
        # Download files
        for file_url,file_name in zip(file_urls,out_paths):
            target_dir = os.path.dirname(file_name)
            if os.path.isdir(target_dir):
                pass
            else:
                os.makedirs(target_dir)

            if os.path.isfile(file_name):
                print(f"{file_name} exist.")
            else:
                response = session.get(file_url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as file:
                        file.write(response.content)

                    if pr:
                        print(f"Downloaded: {os.path.basename(file_name)}")
                else:
                    if pr:
                        print(f"Failed to download: {os.path.basename(file_name)}")

        # Close the session
        session.close()

    if out_dir != None:
        if os.path.isdir(out_dir):
            pass
        else:
            os.makedirs(out_dir)

        # Download files
        for file_url in file_urls:
            file_name = os.path.basename(file_url)
            file_name = os.path.join(out_dir,file_name)

            if os.path.isfile(file_name):
                print(f"{file_name} exist.")
            else:
                response = session.get(file_url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as file:
                        file.write(response.content)
                    
                    if pr:
                        print(f"Downloaded: {os.path.basename(file_name)}")
                else:
                    if pr:
                        print(f"Failed to download: {os.path.basename(file_name)}")

        # Close the session
        session.close()




if __name__=="__main__":
    # url = "https://suntoday.lmsal.com/sdomedia/SunInTime/2018/09/10/f0193.jpg"
    # file = download_from_url(url,"/home/biswanath/test2.jpg")
    # print(file)
    pass