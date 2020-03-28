#!/usr/bin/env python3

import math
import json

#pip install pillow
from PIL import Image, ImageDraw, ImageFont

IMG_DIR = 'C:\\Users\\Lenart\\Documents\\MEGA\\Code\\SquadMinimaps'
FLAG_DIR = 'C:\\Users\\Lenart\\Documents\\MEGA\\Code\\SquadMinimaps\\flags'
MAP_LAYER = 'Sumari_AAS_v1'
TILES = 4
RES = 4096
DRAW_FLAG = True
TEAM_1 = 'gb'
TEAM_2 = 'insurgents'

# Used to translate world space coordinates to image coordinates
def make_wti_interpolater(in_min, in_max, out_min, out_max): 
    in_span = in_max - in_min  
    out_span = out_max - out_min  

    scale_factor = float(out_span) / float(in_span) 

    def interp_fn(value):
        return (value - in_min) * scale_factor + out_min

    return interp_fn


def centered_text(draw, font, text, x, y):
    size = draw.textsize(text, font, stroke_width=5)
    n_x = x - size[0]/2
    n_y = y - size[1]/2
    draw.text((n_x, n_y), font=font, text=text, fill=(255, 255, 255), stroke_fill=(0, 0, 0), stroke_width=5)

def main():
    minimap = Image.new('RGBA', (TILES * RES, TILES * RES), color=(255, 255, 255))

    for x in range(TILES):
        for y in range(TILES):
            path = f'{IMG_DIR}\\{MAP_LAYER}\\{MAP_LAYER}_Minimap-{TILES-x-1}_{TILES-y-1}.TGA'
            print(path)
            tile = Image.open(path)

            minimap.paste(tile, [RES * x, RES * y])


    if DRAW_FLAG:
        font = ImageFont.truetype('arial.ttf', size=72)

        team_flags = [
            Image.open(f'{FLAG_DIR}\\neutral_flag.TGA'),
            Image.open(f'{FLAG_DIR}\\{TEAM_1}_flag.TGA'),
            Image.open(f'{FLAG_DIR}\\{TEAM_2}_flag.TGA')
        ]
        for i in range(3):
            team_flags[i] = team_flags[i].resize(
                [s * 3 for s in team_flags[i].size]
            )

        with open(f'{IMG_DIR}\\{MAP_LAYER}\\{MAP_LAYER}_flags.json', 'r') as fh:
            flag_data = json.load(fh)

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


        draw = ImageDraw.Draw(minimap)

        for flag_id, flag in flag_data['flags'].items():
            for obj_name, bbox in flag['bounds'].items():
                if 'sphere' in obj_name.lower():
                    x = wti_itp_x(bbox['origin']['x'])
                    y = wti_itp_y(bbox['origin']['y'])
                    r = wti_itp_x(flag_data['corner_1']['x'] + bbox['box_extent']['x'])
                    draw.arc(
                        [x - r/2, y - r/2
                        ,x + r/2, y + r/2],
                        0, 360,
                        fill=(0, 0, 255),
                        width=20
                    )
                elif 'box' in obj_name.lower():
                    x = wti_itp_x(bbox['origin']['x'])
                    y = wti_itp_y(bbox['origin']['y'])
                    b_x = wti_itp_x(flag_data['corner_1']['x'] + bbox['box_extent']['x'])
                    b_y = wti_itp_y(flag_data['corner_1']['y'] + bbox['box_extent']['y'])
                    r = math.radians(bbox['rotation'])

                    draw.rectangle(
                        [x - b_x + math.cos(r) * b_x, y - b_y + math.sin(r) * b_y
                        ,x + b_x + math.cos(r) * b_x, y + b_y + math.cos(r) * b_y],
                        outline=(0, 0, 255),
                        width=10
                    )


            if flag['next_flag']:
                x = wti_itp_x(flag['location']['x'])
                y = wti_itp_y(flag['location']['y'])
                next_flag_loc = flag_data['flags'][flag['next_flag']]['location']
                n_x = wti_itp_x(next_flag_loc['x'])
                n_y = wti_itp_y(next_flag_loc['y'])
                print('draw line')
                draw.line( [x, y, n_x, n_y], fill=(128, 128, 128), width=20)

        for flag_id, flag in flag_data['flags'].items():
            x = wti_itp_x(flag['location']['x'])
            y = wti_itp_y(flag['location']['y'])
            print('new flag')
            minimap.alpha_composite(team_flags[int(flag['initial_team'])],
                (int(x - team_flags[int(flag['initial_team'])].size[0]/2),
                 int(y - team_flags[int(flag['initial_team'])].size[1]/2))
            )
            centered_text(draw, font, flag['display_name'], x, y)


    minimap = minimap.convert('RGB')
    minimap.save(f'{IMG_DIR}\\{MAP_LAYER}_stitched.jpg', 'JPEG', quality=90)

if __name__ == "__main__":
    main()

