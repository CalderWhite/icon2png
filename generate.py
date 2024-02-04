import argparse
from multiprocessing import Pool
import os
import sys

from PIL import Image
from tqdm import tqdm

# NOTE: You may have to call: ulimit -Sn 10000
#       To avoid max open files limit.


arg_parser = argparse.ArgumentParser(
    description='Given an arbitrary set of icons, generate a recreation '
                'of any PNG/JPEG using ONLY those icons.'
)
arg_parser.add_argument('-c', '--icon-dir', type=str, required=True,
                    help='The directory where icons are stored')
arg_parser.add_argument('-i', '--input', type=str, default='in.png',
                    help='The output file name (default: "in.png")')
arg_parser.add_argument('-o', '--output', type=str, default='out.png',
                    help='The output file name (default: "out.png")')


def calc_avg_color(img, transparency_color=(255, 255, 255), start_coords=(0, 0), stop_coords=(-1, -1)):
    """ All coordinates are in (rows, cols) """
    img = img.convert('RGBA')
    total_r, total_g, total_b = 0, 0, 0
    width, height = img.size

    original = stop_coords[0]
    if stop_coords[0] == -1 or stop_coords[1] == -1:
        stop_coords = (height, width)

    for y in range(start_coords[0], stop_coords[0]):
        for x in range(start_coords[1], stop_coords[1]):
            r, g, b, a = img.getpixel((x, y))
            if a == 0:
                r, g, b = transparency_color
            else:
                # If the pixel is not fully opaque, blend it with transparency_color
                # NOTE: This will remain untested. Ideally this code does not run.
                r = r + (255 - r) * (transparency_color[0] - a) // 255
                g = g + (255 - g) * (transparency_color[1] - a) // 255
                b = b + (255 - b) * (transparency_color[2] - a) // 255
            total_r += r
            total_g += g
            total_b += b
   
    num_pixels = (stop_coords[0] - start_coords[0]) * (stop_coords[1] - start_coords[1])
    average_r = total_r / num_pixels
    average_g = total_g / num_pixels
    average_b = total_b / num_pixels
    
    return average_r, average_g, average_b


def load_icon(args):
    path, image_fn = args
    image_path = f'{path}/{image_fn}'
    image = Image.open(image_path)
    avg_color = calc_avg_color(image)
    return (avg_color, image_fn)


def load_icons(path):
    print("Loading icons...")
    p = Pool()
    args = [(path, image_fn) for image_fn in os.listdir(path)]
    res = []
    for ret in tqdm(p.imap_unordered(load_icon, args), total=len(args)):
        res.append(ret)

    return res


def gen_paste(args):
    icon_size = 32
    coords, path, in_path, icon_arr = args
    row, col = coords
    avg_color = calc_avg_color(
        Image.open(in_path),
        start_coords=coords,
        stop_coords=(row + icon_size, col + icon_size)
    )

    # NOTE: O(n) scan, very slow. Probably a better way to approximate this in better time complexity
    res_icon_fn = None
    best_diff = float('inf')
    ir, ig, ib = avg_color
    for icon_avg_color, icon_fn in icon_arr:
        r, g, b = icon_avg_color
        diff = abs(r - ir) + abs(g - ig) + abs(b - ib)
        if diff < best_diff:
            best_diff = diff
            res_icon_fn = icon_fn

    return (res_icon_fn, col, row)


def generate_image(icon_dir, in_path, out_path):
    colors_and_icons = load_icons(icon_dir)

    # NOTE: bad hack. All icons must be square and 32x32
    icon_size = 32
    img = Image.open(in_path)
    COLS, ROWS = img.size
    quantized_starts = [(row, col) for col in range(0, COLS, icon_size) for row in range(0, ROWS, 32)]
    args = [(coords, icon_dir, in_path, colors_and_icons) for coords in quantized_starts]
    p = Pool()
    pastes = []
    print("Quantizing image...")
    for res in tqdm(p.imap_unordered(gen_paste, args), total=len(args)):
        pastes.append(res)

    output_image = Image.new('RGBA', (COLS, ROWS), (255, 255, 255, 255))
    for image_path, x, y in pastes:
        with Image.open(f'{icon_dir}/{image_path}') as img:
            output_image.paste(img, (x, y), img)
    output_image.save(out_path)


def main(argv):
    if len(sys.argv) == 1:
        arg_parser.print_help(sys.stderr)
        return

    args = arg_parser.parse_args()
    generate_image(args.icon_dir, args.input, args.output)


if __name__ == '__main__':
    main(sys.argv[1:])
