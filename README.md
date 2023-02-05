# Screenshot Swiper

Screenshots that are automatically uploaded to publicly accessible servers can be easilly accessed by "guessing" random IDs in the right format.

This tool demonstrates this by providing a simple GUI that can be used to explore public accessible screenshots.

## Setup

Create a virtual Python 3 environment and activate it:

```
python -m venv venv && source venv/bin/activate
```

Install the required dependencies:

```
pip install -r requirements.txt
```

Run the swiper script:

```
python screenshot_swiper.py
```

## Usage

The swiper will start at the first accessible screenshot starting with id `100000`. From there you can switch to the next / previous accessible screenshot with the right / left arrow key.

The currently displayed screenshot can be saved by pressing the `s` key.

Press `q` to exit.
