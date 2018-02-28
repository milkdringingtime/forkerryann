import multiprocessing
import os
import pickle
import re
import sys

import urllib3
from imgurpython import ImgurClient
from imgurpython.imgur.models.gallery_album import GalleryAlbum
from imgurpython.imgur.models.gallery_image import GalleryImage

_TAG = "forkerryann"
# _IMAGES_FOLDER = "images2"
_THREAD_COUNT = 8
_LINKS_FILE = "links"


def get_links(tagged):
    links = []
    for item in tagged.items:
        if isinstance(item, GalleryAlbum):
            links.extend(get_links_from_gallery(item))
        elif isinstance(item, GalleryImage):
            links.append(item.link)
    return links


def get_links_from_gallery(gallery):
    links = []
    for img in gallery.images:
        links.append(img["link"])
    return links


def save_to_file(links):
    with open(_LINKS_FILE, mode="wb+") as file:
        pickle.dump(obj=links, file=file)


def get_all_links(client_id, client_secret):
    """
    get all links for images with given tag
    :return:
    """
    client = ImgurClient(client_id=client_id, client_secret=client_secret)

    tagged = client.gallery_tag(tag=_TAG, window="all")

    links = []

    page = 0
    try:
        while True:
            links.extend(get_links(tagged))
            page += 1
            tagged = client.gallery_tag(tag=_TAG, window="all", page=page)
            print(page)
    except:
        print("end of line")

    save_to_file(links)
    print(links)


def load_from_file():
    with open(_LINKS_FILE, mode="rb") as file:
        obj = pickle.load(file=file)
    return obj


def get_filename(link):
    pattern = re.compile(r"imgur\.com/(.*)")
    return re.search(pattern, link).group(1)


http = urllib3.PoolManager(num_pools=_THREAD_COUNT)


def process_url(url):
    print(f"processing {url}")
    location = f"{_TAG}/{get_filename(url)}"

    resp = http.request('GET', url)

    with open(file=location, mode="wb") as file:
        file.write(resp.data)


def download_images():
    links = load_from_file()
    print(f"downloading {len(links)} files")

    if not os.path.exists(_TAG):
        os.makedirs(_TAG)

    pool = multiprocessing.Pool(processes=_THREAD_COUNT)
    pool.map(process_url, links)


if __name__ == '__main__':
    args = sys.argv
    client_id = args[1]
    client_secret = args[2]

    get_all_links(client_id, client_secret)
    download_images()
