import os
import requests
import cloudscraper
import tkinter as tk
from io import BytesIO
from PIL import ImageTk
from PIL import Image
from bs4 import BeautifulSoup

# config
BASE_URL = "https://prnt.sc/"
SAVE_FOLDER = "./saved/"
SAVE_FILE = ".current_id"
STARTING_ID = "100000"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0)"
        " Gecko/20100101 Firefox/93.0",
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers",
}

image_label = None
current_image = None


def get_screenshot(scraper, id):
    image_url = BASE_URL + id

    soup = BeautifulSoup(scraper.get(image_url).text, "html.parser")
    image_url = soup.find_all(id="screenshot-image")[0]["src"]

    # no screenshot available for this id
    if image_url.startswith("//st.prntscr"):
        return None

    screenshot = requests.get(image_url).content

    # no screenshot available for this id
    if screenshot.startswith(b"<html>"):
        return None

    return screenshot


def save_current_id(current_id):
    save_path = SAVE_FOLDER + SAVE_FILE
    with open(save_path, "w") as f:
        f.write(current_id)


def get_current_id():

    save_path = SAVE_FOLDER + SAVE_FILE

    if os.path.isfile(save_path):
        with open(save_path, "r") as f:
            id = f.readline().strip()
            return id

    save_current_id(STARTING_ID)
    return STARTING_ID


def next_id(current_id):
    # increase the given id according to the naming pattern
    # naming pattern: 6-digit 0-9, a-z

    new_id = ""
    adding = True

    for digit in current_id[::-1]:
        if not adding:
            new_id = digit + new_id
            continue

        # if digit is 0-8 or a-y: increase to next digit and stop adding
        if ord(digit) in range(ord("0"), ord("9")) or ord(digit) in range(
            ord("a"), ord("z")
        ):
            new_digit = chr(ord(digit) + 1)
            adding = False
        elif digit == "9":  # at 9, switch to lower alphabet
            new_digit = "a"
            adding = False
        elif digit == "z":  # at z, wrap back to 0 and carry on adding
            new_digit = "0"

        new_id = new_digit + new_id

    save_current_id(new_id)

    return new_id


def prev_id(current_id):

    if current_id == STARTING_ID:
        return current_id

    new_id = ""
    subtracting = True

    for digit in current_id[::-1]:
        if not subtracting:
            new_id = digit + new_id
            continue

        # if digit is 1-9 or b-z: decrease to next digit and stop subtracting
        if ord(digit) in range(ord("1"), ord("9") + 1) or ord(digit) in range(
            ord("b"), ord("z") + 1
        ):
            new_digit = chr(ord(digit) - 1)
            subtracting = False
        elif digit == "a":  # at a, switch to digits
            new_digit = "9"
            subtracting = False
        elif digit == "0":  # at z, wrap back to 0 and carry on adding
            new_digit = "z"

        new_id = new_digit + new_id

    save_current_id(new_id)

    return new_id


def gui_set_screenshot(forward, scraper, root):
    global image_label, current_image

    # get current id from file
    current_id = get_current_id()

    # move forward or backward until next valid screenshot is found
    current_image = None
    while current_image is None:
        if forward:
            current_id = next_id(current_id)
        else:
            current_id = prev_id(current_id)
        current_image = get_screenshot(scraper, current_id)

    # update title
    root.title(f"Screenshot Swiper - {current_id}")

    # create image object for tkinter
    screenshot_image = ImageTk.PhotoImage(Image.open(BytesIO(current_image)))

    # resize
    image_width = screenshot_image.width()
    image_height = screenshot_image.height()
    x = 0
    y = 0
    root.geometry(f"{image_width}x{image_height}+{x}+{y}")

    # insert image into window
    image_label.configure(image=screenshot_image)
    image_label.image = screenshot_image

    root.eval("tk::PlaceWindow . center")


def save_current_screenshot():
    global current_image

    current_id = get_current_id()

    save_path = f"{SAVE_FOLDER}{current_id}.png"

    with open(save_path, "wb") as f:
        f.write(current_image)


def main():
    global image_label, current_image
    # check if save folder exists and if not create it
    if not os.path.isdir(SAVE_FOLDER):
        os.mkdir(SAVE_FOLDER)

    # load current id from save if exists
    current_id = get_current_id()

    # initialize scraper
    scraper = cloudscraper.create_scraper()

    # load screenshot from current id with scraping method
    current_image = get_screenshot(scraper, current_id)
    while current_image is None:
        current_id = next_id(current_id)
        current_image = get_screenshot(scraper, current_id)

    root = tk.Tk()

    root.title(f"Screenshot Swiper - {current_id}")

    screenshot_image = ImageTk.PhotoImage(Image.open(BytesIO(current_image)))

    # resize
    image_width = screenshot_image.width()
    image_height = screenshot_image.height()
    x = 0
    y = 0
    root.geometry(f"{image_width}x{image_height}+{x}+{y}")

    # insert image into window
    image_label = tk.Label(root, image=screenshot_image)
    image_label.pack(side="top", fill="both", expand="yes")

    root.bind("<Escape>", lambda x: root.destroy())
    root.bind("q", lambda x: root.destroy())
    root.bind("s", lambda x: save_current_screenshot())
    root.bind("<Right>", lambda x: gui_set_screenshot(True, scraper, root))
    root.bind("<Left>", lambda x: gui_set_screenshot(False, scraper, root))

    root.eval("tk::PlaceWindow . center")

    root.mainloop()

    return


if __name__ == "__main__":
    main()
