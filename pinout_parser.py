#!/bin/python
import sys, csv

if len(sys.argv) < 2:
    print('Usage: python pinout_parser.py <pinout.csv> [package]')
    print('Example: python pinout_parser.py ECP5UM5G-85Pinout.csv CABGA756')
    print("Don't forget to zoom out :)")
    exit()

pins = [] # Pad Name Bank Dual_Function Differential High_Speed DQS Ball M N
# Differential: Either False or a list with the name of the other pin and the polarity of this pin
# High_Speed: True, False

device_name = ''

if len(sys.argv) == 3:
    package = sys.argv[2]
else:
    package = 'CABGA381'

max_m = 0
max_n = 0
# Maps ball letter to n number
ball_names = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R', 'T', 'U',
    'V', 'W', 'Y', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AJ', 'AK', 'AL', 'AM',
    ]

ball_number = {ball_names[i] : i + 1 for i in range(len(ball_names))}
ball_name = {v: k for k, v in ball_number.items()}

with open(sys.argv[1]) as file:
    reader = csv.reader(file)
    index = 0
    package_index = 0

    for row in reader:
        index += 1

        if index > 5:
            this_ball = row[package_index]
            if this_ball != '-':
                try:
                    m = int(this_ball[1:])
                    n = ball_number[this_ball[0]]
                except:
                    m = int(this_ball[2:])
                    n = ball_number[this_ball[:2]]

                
                max_m = max(max_m, m)
                max_n = max(max_n, n)

                pins.append([
                    *row[0:3],
                    False if row[3] == '-' else row[3],
                    False if row[4] == '-' else [row[4].split('_OF_')[1], row[4][:4] == 'True'],
                    row[5] == True,
                    row[6],
                    this_ball,
                    m,
                    n,
                    ])

        
        elif index == 5:
            for value in row:
                if value == package:
                    break
                package_index += 1

        elif index == 1:
            device_name = row[0].split(' ')[-1]

# Colors
fg_default = '255;255;255'
bg_default = '0;0;0'
fg_gnd = '255;255;255'
bg_gnd = '31;31;31'
fg_vcc = '0;0;0'
bg_vcc = '255;31;31'
fg_nc = '95;95;95'
bg_nc = '0;0;0'
fg_cfg = '0;0;0'
bg_cfg = '255;127;31'
fg_signal = '255;255;255'
bg_signal_p = '95;31;31'
bg_signal_n = '31;31;95'
fg_clk = '0;0;0'
bg_clk = '31;255;31'
fg_jtag = '0;0;0'
bg_jtag = '255;255;31'
fg_refclk = '0;0;0'
bg_refclk_p = '127;255;127'
bg_refclk_n = '95;192;95'
fg_hdtx = '255;255;255'
bg_hdtx_p = '255;127;127'
bg_hdtx_n = '192;95;95'
fg_hdrx = '255;255;255'
bg_hdrx_p = '127;127;255'
bg_hdrx_n = '95;95;192'

colors = {
    "VCC" : [fg_vcc, bg_vcc], "GND" : [fg_gnd, bg_gnd],
    "Config" : [fg_cfg, bg_cfg], "JTAG" : [fg_jtag, bg_jtag],
    "Signal +" : [fg_signal, bg_signal_p], "Signal -" : [fg_signal, bg_signal_n],
    "Clock" : [fg_clk, bg_clk],
    "REFCLK +" : [fg_refclk, bg_refclk_p], "REFCLK -" : [fg_refclk, bg_refclk_n],
    "TX +" : [fg_hdtx, bg_hdtx_p], "TX -" : [fg_hdtx, bg_hdtx_n],
    "RX +" : [fg_hdrx, bg_hdrx_p], "RX -" : [fg_hdrx, bg_hdrx_n],
}


def get_ball_desc(pin_data):
    if pin_data == None:
        return ['█' * 8] * 4
    
    empty = '        '
    lines = [empty] * 4

    lines[0] = '{:<7}'.format(pin_data[1][:7]) + (pin_data[2] if pin_data[2] != '40' else 'X') # Name and Bank
    lines[1] = ('{:<6}'.format(pin_data[4][0]) if pin_data[4] else '      ') + ('HS' if pin_data[5] else '  ')

    fg = fg_default
    fg2 = False
    bg = bg_default
    bg2 = False

    if pin_data[1][0] == 'V' or pin_data[1] == 'GND':
        if pin_data[1][0:4] == "VCCH":
            lines[0] = pin_data[1][0:7]
            lines[1] = pin_data[1][8:]
        else:
            lines[0] = pin_data[1]
        if pin_data[1] == 'GND':
            lines[0] = 'GND'
            fg = fg_gnd
            bg = bg_gnd
        else:
            fg = fg_vcc
            bg = bg_vcc
        
            if pin_data[1][:5] == 'VCCIO':
                lines[0] = 'VCCIO'
                lines[1] = 'Bank %s' % pin_data[1][5]
            elif pin_data[1] == 'VCCAUX':
                lines[0] = 'VCCAUX'

        lines[3] = 'Power'

    elif pin_data[1] == 'NC':
        #l1 = '▀▄    ▄▀'
        #l2 = '  ▀▄▄▀  '
        #l3 = '  ▄▀▀▄  '
        #l4 = '▄▀    ▀▄'
        fg = fg_nc
        bg = bg_nc
        lines[0] = '██▄NC▄██'
        lines[1] = ' ▀████▀ '
        lines[2] = ' ▄████▄ '
        lines[3] = '██▀  ▀██'

    elif pin_data[1][:3] == 'CFG' or pin_data[1] in ['CCLK', 'INITN', 'PROGRAMN', 'DONE']:
        lines[0] = pin_data[1]
        lines[3] = 'Config'
        fg = fg_cfg
        bg = bg_cfg
    
    # Dual use pins
    elif pin_data[3] and ('/' in pin_data[3] or pin_data[3] in ['WRITEN']):
        fg2 = fg_cfg
        bg2 = bg_cfg
        lines[2] = '{:<16}'.format(pin_data[3])[0:8]
        lines[3] = '{:<16}'.format(pin_data[3])[8:16]
        if pin_data[4]:
            if pin_data[4][1]:
                bg = bg_signal_p
            else:
                bg = bg_signal_n

    # Clock inputs
    elif pin_data[3] and ('GPLL' in pin_data[3] or 'CLK' in pin_data[3]): # It needs the parentheses for some reason
        fg2 = fg_clk
        bg2 = bg_clk
        lines[2] = '{:<16}'.format(pin_data[3])[0:8]
        lines[3] = '{:<16}'.format(pin_data[3])[8:16]
        if pin_data[4]:
            if pin_data[4][1]:
                bg = bg_signal_p
            else:
                bg = bg_signal_n

    elif pin_data[1][0] == 'P':
        lines[3] = 'Signal'
        fg = fg_signal
        if pin_data[4]:
            if pin_data[4][1]:
                bg = bg_signal_p
            else:
                bg = bg_signal_n
        
        if pin_data[3]:
            lines[2] = '{:<16}'.format(pin_data[3])[0:8]
            lines[3] = '{:<16}'.format(pin_data[3])[8:16]

    elif pin_data[1][0] == 'T':
        fg = fg_jtag
        bg = bg_jtag
        lines[0] = lines[0][:7]
        lines[3] = 'JTAG' #\x1b also works

    elif pin_data[1][:6] == 'REFCLK':
        lines[0] = 'REFCLK'
        lines[1] = pin_data[1][8:]
        fg = fg_refclk
        if pin_data[1][6] == 'P':
            bg = bg_refclk_p
        elif pin_data[1][6] == 'N':
            bg = bg_refclk_n

    elif pin_data[1][:2] == 'HD':
        lines[0] = pin_data[1][2:5]
        lines[1] = pin_data[1][7:]
        if pin_data[1][2:4] == 'TX':
            fg = fg_hdtx
            if pin_data[1][4] == 'P':
                bg = bg_hdtx_p
            elif pin_data[1][4] == 'N':
                bg = bg_hdtx_n
                
        elif pin_data[1][2:4] == 'RX':
            fg = fg_hdrx
            if pin_data[1][4] == 'P':
                bg = bg_hdrx_p
            elif pin_data[1][4] == 'N':
                bg = bg_hdrx_n

    else:
        lines[3] = pin_data[1][:8]
    
    cstr = '\033[38;2;' + fg + 'm' + '\033[48;2;' + bg + 'm'
    cstr2 = '\033[38;2;' + (fg2 if fg2 else fg) + 'm' + '\033[48;2;' + (bg2 if bg2 else bg) + 'm'
    end = '\033[0m'

    for i in range(4):
        line = '{:<8}'.format(lines[i][:8])
        lines[i] = cstr + (line[:7 - i * 2] + cstr2 + line[7 - i * 2:8] if fg2 or bg2 else line) + end

    return lines


grid = [[None] * max_n for _ in range(max_m)]

for pin in pins:
    grid[pin[8] - 1][pin[9] - 1] = pin

print('    ██', end='')
print('        ██' * max_m)
print('    ██', end='')
for m in range(max_m):
    print('   {:<2}   ██'.format(m + 1), end='')

print()

for n in range(max_n):
    print('█' * (10 * max_m + 6))
    lines = [''] * 4
    for m in range(max_m):
        parts = get_ball_desc(grid[m][n])
        for i in range(4):
            lines[i] += '██' + parts[i]

    for i in range(4):
        print(' {:>2}'.format(ball_name[n + 1]) + ' ' + lines[i] + '██')



print('█' * (10 * max_m + 6))
print()

print('█' * (10 * len(colors.items()) + 2))
lines = [''] * 4
for name, color in colors.items():
    parts = get_ball_desc(grid[m][n])
    for i in range(1):
        cstr = '\033[38;2;' + color[0] + 'm' + '\033[48;2;' + color[1] + 'm'
        end = '\033[0m'
        print('██' + cstr + '{:<8}'.format(name) + end, end='')

print('██')
print('█' * (10 * len(colors.items()) + 2))
print()
print('Device Name: ' + device_name)
print('Package: ' + package)