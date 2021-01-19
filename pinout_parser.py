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


def get_ball_desc(pin_data):
    if pin_data == None:
        return ['█' * 8] * 4
    
    empty = '        '
    lines = [empty] * 4

    lines[0] = '{:<7}'.format(pin_data[1][:7]) + (pin_data[2] if pin_data[2] != '40' else 'X') # Name and Bank
    lines[1] = ('{:<6}'.format(pin_data[4][0]) if pin_data[4] else '      ') + ('HS' if pin_data[5] else '  ')

    fg = '255;255;255'
    bg = '0;0;0'

    if pin_data[1][0] == 'V' or pin_data[1] == 'GND':
        if pin_data[1] == 'GND':
            lines[0] = 'GND     '
            bg = '31;31;31'
        else:
            fg = '0;0;0'
            bg = '255;31;31'
        
            if pin_data[1][:5] == 'VCCIO':
                lines[0] = 'VCCIO   '
                lines[1] = 'Bank %s  ' % pin_data[1][5]
            elif pin_data[1] == 'VCCAUX':
                lines[0] = 'VCCAUX  '

        lines[3] = 'Power   '

    elif pin_data[1] == 'NC':
        #l1 = '▀▄    ▄▀'
        #l2 = '  ▀▄▄▀  '
        #l3 = '  ▄▀▀▄  '
        #l4 = '▄▀    ▀▄'
        fg = '100;100;100'
        lines[0] = '██▄NC▄██'
        lines[1] = ' ▀████▀ '
        lines[2] = ' ▄████▄ '
        lines[3] = '██▀  ▀██'

    elif pin_data[1][0] == 'P':
        lines[3] = 'Signal'
        if pin_data[4]:
            if pin_data[4][1]:
                bg = '95;31;31'
            else:
                bg = '31;31;95'
        
        if pin_data[3]:
            lines[2] = '{:<16}'.format(pin_data[3])[0:8]
            lines[3] = '{:<16}'.format(pin_data[3])[8:16]

    elif pin_data[1][:3] == 'CFG':
        lines[3] = 'Config'
        bg = '255;127;31'
        fg = '0;0;0'

    elif pin_data[1][0] == 'T':
        fg = '0;0;0'
        bg = '255;255;31'
        lines[0] = lines[0][:7]
        lines[3] = 'JTAG' #\x1b also works

    elif pin_data[1][:6] == 'REFCLK':
        lines[0] = 'REFCLK'
        lines[1] = pin_data[1][8:]
        bg = '63;255;63'
        fg = '0;0;0'
        if pin_data[1][6] == 'P':
            bg = '127;255;127'
        elif pin_data[1][6] == 'N':
            bg = '95;192;95'

    elif pin_data[1][:2] == 'HD':
        lines[0] = pin_data[1][2:5]
        lines[1] = pin_data[1][7:]
        if pin_data[1][2:4] == 'TX':
            if pin_data[1][4] == 'P':
                bg = '255;127;127'
            elif pin_data[1][4] == 'N':
                bg = '192;95;95'
                
        elif pin_data[1][2:4] == 'RX':
            if pin_data[1][4] == 'P':
                bg = '127;127;255'
            elif pin_data[1][4] == 'N':
                bg = '95;95;192'

    else:
        lines[3] = pin_data[1][:8]
    
    cstr = '\033[38;2;' + fg + 'm' + '\033[48;2;' + bg + 'm'
    end = '\033[0m'

    for i in range(4):
        lines[i] = cstr + '{:<8}'.format(lines[i][:8]) + end

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
print('Device Name: ' + device_name)
print('Package: ' + package)