# icon2png

<img width="857" alt="Screenshot 2024-02-04 at 6 37 42 PM" src="https://github.com/CalderWhite/icon2png/assets/15067287/224e2d5c-7a15-498d-8b9f-5c2dd516bf88">


Given an arbitrary set of icons, generate a recreation of any PNG/JPEG using ONLY those icons.

This is what I used to create my submission to the [wabi-sabi-thon](https://lu.ma/wst).


# Usage

First run

```
pip3 install -r requirements.txt
```

Then run the command line tool. Here is the help message:

```
$ python3 generate.py --help
usage: generate.py [-h] -c ICON_DIR [-i INPUT] [-o OUTPUT]

Given an arbitrary set of icons, generate a recreation of any PNG/JPEG using ONLY those icons.

options:
  -h, --help            show this help message and exit
  -c ICON_DIR, --icon-dir ICON_DIR
                        The directory where icons are stored
  -i INPUT, --input INPUT
                        The output file name (default: "in.png")
  -o OUTPUT, --output OUTPUT
                        The output file name (default: "out.png")
```
