#!/usr/bin/env python3

import math
import json

#pip install pillow
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops


# Settings

# Folder names can be relative to the script execution location or absolute

# Name of the layer folder located inside the IMG_DIR
# master folder which contains tiled images and flag json
MAP_LAYER = 'Sumari_AAS_v1'
# Same number as when creating the minimap inside the editor
TILES = 4
# Resolution of the tile not image
RES = 4096
DRAW_FLAG = True
DRAW_CAPTURE_ZONE = True
DRAW_BORDER = True


# Master folder which contains layer folders with images of layers and flag json
IMG_DIR = ''
# Folder which contains flag images and roboto default font
RESOURCES_DIR = 'resources'

# Used to translate faction name to its flag image file name
faction_to_image = {
    'GB' : 'gb',
    'INS' : 'insurgents',
    'MIL' : 'militia',
    'RUS' : 'russia',
    'USA' : 'usa'
}


# Used to translate world space coordinates to image coordinates
def make_wti_interpolater(in_min, in_max, out_min, out_max): 
    in_span = in_max - in_min  
    out_span = out_max - out_min  

    scale_factor = float(out_span) / float(in_span) 

    def interp_fn(value):
        return (value - in_min) * scale_factor + out_min

    return interp_fn

# Function to draw text so that x,y is in the middle of the draw text
def centered_text(draw, font, text, x, y):
    size = draw.textsize(text, font, stroke_width=5)
    n_x = x - size[0]/2
    n_y = y - size[1]/2
    draw.text((n_x + 3, n_y + 3), font=font, text=text, fill=(0, 0, 0), stroke_fill=(0, 0, 0), stroke_width=1)
    draw.text((n_x, n_y), font=font, text=text, fill=(255, 255, 255))

def main():
    # Create target image
    minimap = Image.new('RGBA', (TILES * RES, TILES * RES), color=(255, 255, 255))

    # Stitch image
    for x in range(TILES):
        for y in range(TILES):
            file_name = f'{MAP_LAYER}_Minimap-{TILES-x-1}_{TILES-y-1}.TGA'
            print(f'Stitching {file_name}')
            path = f'{IMG_DIR}\\{MAP_LAYER}\\{file_name}'
            tile = Image.open(path)

            minimap.paste(tile, [RES * x, RES * y])


    if DRAW_FLAG or DRAW_CAPTURE_ZONE or DRAW_BORDER:
        # Load flag data json
        with open(f'{IMG_DIR}\\{MAP_LAYER}\\{MAP_LAYER}_flags.json', 'r') as fh:
            flag_data = json.load(fh)

        # Make world to picture coordinates interpolaters
        wti_itp_x = make_wti_interpolater(
            flag_data['corner_1']['x'],
            flag_data['corner_2']['x'],
            0,
            RES * TILES
        )

        wti_itp_y = make_wti_interpolater(
            flag_data['corner_1']['y'],
            flag_data['corner_2']['y'],
            0,
            RES * TILES
        )

    if DRAW_CAPTURE_ZONE:
        zones_overlay = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 0))
        zones_draw = ImageDraw.Draw(zones_overlay)
        
        for _, flag in flag_data['flags'].items():
            print(f'Draw zone for {flag["display_name"]}')
            for obj_name, bbox in flag['bounds'].items():
                # Draw a spherical bounding box (circle)
                if 'sphere' in obj_name.lower():
                    x = wti_itp_x(bbox['origin']['x'])
                    y = wti_itp_y(bbox['origin']['y'])
                    r = wti_itp_x(flag_data['corner_1']['x'] + bbox['radius'])
                    zones_draw.ellipse(
                        [x - r/2, y - r/2
                        ,x + r/2, y + r/2],
                        fill=(0, 0, 255, 255),
                    )
                # Draw a square bounding box (rectangle)
                elif 'box' in obj_name.lower():
                    x = wti_itp_x(bbox['origin']['x'])
                    y = wti_itp_y(bbox['origin']['y'])
                    b_x = wti_itp_x(flag_data['corner_1']['x'] + bbox['box_extent']['x'])
                    b_y = wti_itp_y(flag_data['corner_1']['y'] + bbox['box_extent']['y'])
                    r = 180 - bbox['rotation']

                    rectangle = Image.new('RGBA', (int(b_x) * 2, int(b_y) * 2), color=(0, 0, 255, 255) )
                    rectangle = rectangle.rotate(r, expand=True, fillcolor=(0, 0, 0, 0))

                    zones_overlay.alpha_composite(
                        rectangle,
                        (int(x - rectangle.size[0]/2),
                         int(y - rectangle.size[1]/2))
                    )

        print('Compositing zones to image')
        transparency = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 196))
        zones_overlay = ImageChops.subtract(zones_overlay, transparency)
        minimap.alpha_composite(zones_overlay)

    if DRAW_FLAG:
        # Create font object
        font = ImageFont.truetype(f'{RESOURCES_DIR}\\Roboto-Regular.ttf', size=72)

        # Load team flags
        team_flags = [
            Image.open(f'{RESOURCES_DIR}\\neutral_flag.TGA'),
            Image.open(f'{RESOURCES_DIR}\\{ faction_to_image[flag_data["team_one"]] }_flag.TGA'),
            Image.open(f'{RESOURCES_DIR}\\{ faction_to_image[flag_data["team_two"]] }_flag.TGA')
        ]

        # Upscale flags and make them translucent
        for i in range(3):
            team_flags[i] = team_flags[i].resize(
                [s * 3 for s in team_flags[i].size]
            )


        # Create drawing object
        objectives_overlay = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(objectives_overlay)

        # Draw a line connecting objectives
        for _, flag in flag_data['flags'].items():
            if flag['next_flag']:
                print(f'Draw objective line for {flag["display_name"]}')
                x = wti_itp_x(flag['location']['x'])
                y = wti_itp_y(flag['location']['y'])
                next_flag_loc = flag_data['flags'][flag['next_flag']]['location']
                n_x = wti_itp_x(next_flag_loc['x'])
                n_y = wti_itp_y(next_flag_loc['y'])
                draw.line( [x, y, n_x, n_y], fill=(255, 255, 255, 169), width=15)

        # Draw flags and name
        for _, flag in flag_data['flags'].items():
            print(f'Drawing flag for {flag["display_name"]}')
            x = wti_itp_x(flag['location']['x'])
            y = wti_itp_y(flag['location']['y'])
            objectives_overlay.alpha_composite(
                team_flags[flag['initial_team']],

                (int(x - team_flags[int(flag['initial_team'])].size[0]/2),
                 int(y - team_flags[int(flag['initial_team'])].size[1]/2))
            )
            # Draw objective name
            centered_text(draw, font, flag['display_name'], x, y - 150)

        print('Compositing objectives to image')

        transparency = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 55))
        objectives_overlay = ImageChops.subtract(objectives_overlay, transparency)
        minimap.alpha_composite(objectives_overlay)     

    if DRAW_BORDER:
        print('Parsing border line')
        dict_border = {}
        start = None

        # Store unordered line segmets as a hash table where key is start and value is end
        for segment in flag_data['border']:
            s_x = wti_itp_x(segment['start']['x'])
            s_y = wti_itp_y(segment['start']['y'])
            e_x = wti_itp_x(segment['end']['x'])
            e_y = wti_itp_y(segment['end']['y'])
            if not start:
                start = (s_x, s_y)
            dict_border[ (s_x, s_y) ] = ( e_x, e_y )

        # Store line segments in order
        in_order_border = []
        current_point = start
        while True:
            next_point = dict_border[current_point]
            in_order_border += [p for p in current_point] + [p for p in next_point]

            if next_point == start:
                break
            else:
                current_point = next_point

        print('Creating border')
        # Create border mask similar to the one found in squad
        blend_mask = Image.new('RGBA', (TILES * RES, TILES * RES), color=(255, 255, 255, 255))
        bm_draw = ImageDraw.Draw(blend_mask)
        bm_draw.polygon(in_order_border, fill=(0, 0, 0, 0))

        # Blend outside of the border
        border_outside = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 128))
        bo_draw = ImageDraw.Draw(border_outside)
        bo_draw.line(in_order_border, fill=(0, 0, 0, 255), width=100)
        border_outside = border_outside.filter(ImageFilter.BoxBlur(100))

        # Blend inside of the border
        border_inside = Image.new('RGBA', (TILES * RES, TILES * RES), color=(0, 0, 0, 0))
        bi_draw = ImageDraw.Draw(border_inside)
        bi_draw.polygon(in_order_border, fill=(0, 0, 0, 0))
        bi_draw.line(in_order_border, fill=(0, 0, 0, 128), width=50)
        border_inside = border_inside.filter(ImageFilter.BoxBlur(50))
        
        print('Creating border composite')
        border = ImageChops.composite(border_outside, border_inside, blend_mask)
        print('Compositing border to image')
        minimap.alpha_composite(border)

    print('Saving minimap')
    minimap = minimap.convert('RGB')
    minimap.save(f'{IMG_DIR}\\{MAP_LAYER}_stitched.jpg', 'JPEG', quality=90)

if __name__ == "__main__":
    main()
