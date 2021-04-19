#!/bin/python
import sys, csv

try:
    import KicadModTree as kmt
    kicadMod = True
except:
    kicadMod = False

if len(sys.argv) < 2:
    print('Usage: python pinout_parser.py <pinout.csv> [package] [m] [s library file]')
    print('Example: python pinout_parser.py ECP5UM5G-85Pinout.csv CABGA756 s project.lib')
    print('m stands for module / footprint and s stands for symbol')
    print('Don\'t forget to zoom out :)')
    exit()

pins = [] # Pad Name Bank Dual_Function Differential High_Speed DQS Ball M N
# Differential: Either False or a list with the name of the other pin and the polarity of this pin
# High_Speed: True, False

device_name = ''

if 'm' in sys.argv and kicadMod:
    kicadMod = True
else:
    kicadMod = False

if 's' in sys.argv:
    kicadLib = True
    kicadLibFile = sys.argv[sys.argv.index('s') + 1]
else:
    kicadLib = False

if len(sys.argv) >= 3 and len(sys.argv[2]) > 1:
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

pitch = 0.8 # mm

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


pinNames = [pin[1] for pin in pins]

for pin in pins:
    if pin[4]:
        if not pin[4][0] in pinNames:
            pin[4] = False



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
bg_signal = '64;64;64'
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
    'VCC' : [fg_vcc, bg_vcc], 'GND' : [fg_gnd, bg_gnd],
    'Config' : [fg_cfg, bg_cfg], 'JTAG' : [fg_jtag, bg_jtag],
    'Signal' : [fg_signal, bg_signal], 'Signal +' : [fg_signal, bg_signal_p], 'Signal -' : [fg_signal, bg_signal_n],
    'Clock' : [fg_clk, bg_clk],
    'REFCLK +' : [fg_refclk, bg_refclk_p], 'REFCLK -' : [fg_refclk, bg_refclk_n],
    'TX +' : [fg_hdtx, bg_hdtx_p], 'TX -' : [fg_hdtx, bg_hdtx_n],
    'RX +' : [fg_hdrx, bg_hdrx_p], 'RX -' : [fg_hdrx, bg_hdrx_n],
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
        if pin_data[1][0:4] == 'VCCH':
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
        else:
            bg = bg_signal

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
        else:
            bg = bg_signal

    elif pin_data[1][0] == 'P':
        lines[3] = 'Signal'
        fg = fg_signal
        if pin_data[4]:
            if pin_data[4][1]:
                bg = bg_signal_p
            else:
                bg = bg_signal_n
        else:
            bg = bg_signal
        
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



if kicadMod:
    mod = kmt.Footprint(package)
    mod.setDescription(package + ' package')

    border = 1 # 1 mm space around edges, approximately enough for every package
    
    mod.append(kmt.Text(type='reference', text='REF**', at=[(max_m + 1) / 2 * pitch, pitch - border - 3], layer='F.SilkS'))
    mod.append(kmt.Text(type='value', text=package, at=[(max_m + 1) / 2 * pitch, pitch - border - 1], layer='F.Fab'))

    mod.append(kmt.RectLine(start=[pitch - border, pitch - border], end=[(max_m) * pitch + border, (max_n) * pitch + border], layer='F.SilkS'))
    mod.append(kmt.Line(start=[pitch - border, pitch], end=[pitch, pitch - border], layer='F.SilkS'))

    # Courtyard
    mod.append(kmt.RectLine(start=[pitch - border, pitch - border], end=[(max_m) * pitch + border, (max_n) * pitch + border], layer='F.CrtYd'))

    for pin in pins:
        mod.append(kmt.Pad(number=ball_name[pin[9]] + str(pin[8]), type=kmt.Pad.TYPE_SMT, shape=kmt.Pad.SHAPE_CIRCLE, at=[pin[8] * pitch, pin[9] * pitch], size=[pitch / 2, pitch / 2], layers=kmt.Pad.LAYERS_SMT))

    file_handler = kmt.KicadFileHandler(mod)
    file_handler.writeFile(package + '.kicad_mod')


pins.sort(key = lambda pin : pin[2])

if kicadLib:
    pinDict = {pin[1]:pin for pin in pins}

    singleEnded = [pin for pin in pins if not pin[4] and pin[1][0] == 'P' and len(pin[1]) <= 6] # Don't include SERDES
    diffPairs   = [[pin, pinDict[pin[4][0]]] for pin in pins if pin[4] and pin[4][1] and pin[1][0] == 'P' and len(pin[1]) <= 6] # Don't include SERDES
    jtag = [pin for pin in pins if pin[1][0] == 'T']
    cfg = [pin for pin in pins if pin[1][:3] == 'CFG' or pin[1] in ['CCLK', 'INITN', 'PROGRAMN', 'DONE']]
    cfgExtra = [pin for pin in pins if pin[3] and (not 'CCLK' == pin[1] and ('/' in pin[3] or pin[3] in ['WRITEN']))]
    clk = [pin for pin in pins if pin[3] and ('GPLL' in pin[3] or 'CLK' in pin[3]) or 'CK' in pin[1]] # ALL clock signals, even JTAG
    serdesRX = [pin for pin in pins if pin[1][:4] == 'HDRX']
    serdesTX = [pin for pin in pins if pin[1][:4] == 'HDTX']
    refclk = [pin for pin in pins if pin[1][:6] == 'REFCLK']
    power = [pin for pin in pins if pin[1][0] == 'V' or pin[1] == 'GND']

    powerNames = ['GND']
    for pin in power:
        if not pin[1] in powerNames:
            powerNames.append(pin[1])

    banks = []
    for pin in pins:
        if pin[2] != '-' and len(pin[2]) == 1 and not pin[2] in banks:
            banks.append(pin[2])
    
    if False:
        print(len(diffPairs))
        print(len(jtag))
        print(len(cfg))
        print(len(cfgExtra))
        print(len(clk))
        print(len(serdesRX))
        print(len(serdesTX))
        print(len(refclk))
        print(len(power))
        print(len(powerNames))
        print([pin[1] for pin in clk])
        print(powerNames)
    else:
        print("IO:", len(singleEnded) + len(diffPairs) * 2)
        print("Diff. Pairs:", len(diffPairs))
        print("SERDES:", int(len(serdesRX) / 2))
        print("Power Domains:", len(powerNames) - 1)


    template = '''DEF {name} U 0 40 Y Y {units} L N
F0 "U" 0 150 50 H V C CNN
F1 "{name}" 50 0 50 H V C CNN
F2 "{footprint}" 0 0 50 H I C CNN
DRAW
{pins}
ENDDRAW
ENDDEF'''

    unit = 50 # One grid point in KiCad


    pinStr = ''
    part = 1


    #
    # Power
    #
    halfwidth = 10
    pinStr += 'S {0} {1} {2} {3} {4} 1 0 f\n'.format(-unit * halfwidth, -(len(powerNames) - 1) * unit, unit * halfwidth, (len(powerNames) - 1) * unit, part)
    for powerName in powerNames:

        thisPins = [pin for pin in power if pin[1] == powerName]

        if powerName == 'GND':
            x = -(2 + halfwidth) * unit
            y = -(len(powerNames) - 2) * unit
            orientation = 'R'
        else:
            x = (2 + halfwidth) * unit
            y = (-len(powerNames) + 2 * powerNames.index(powerName)) * unit
            orientation = 'L'

        pinStr += 'X {0} ~ {1} {2} 100 {3} 50 50 {4} 1 W\n'.format(powerName, x, y, orientation, part)

        for pin in thisPins:
            pinStr += 'X {0} {1} {2} {3} 100 {4} 50 50 {5} 1 W N\n'.format(powerName, ball_name[pin[9]] + str(pin[8]), x, y, orientation, part)


    #
    # Banks
    #
    halfwidth = 15
    for bank in banks:
        part += 1

        thisPairs = [pin for pin in diffPairs if pin[0][2] == bank]
        thisSE    = [pin for pin in singleEnded if pin[2] == bank]

        x = (3 + halfwidth) * unit
        yMax = 4 * -len(thisPairs) - 1

        pinStr += 'S {0} {1} {2} {3} {4} 1 0 f\n'.format(-unit * halfwidth, -(len(thisPairs) * 2 + len(thisSE) + 2) * unit * 2 + 2 * unit, unit * halfwidth, 0, part)
        pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -unit, part, '"Bank ' + bank + '"')

        if len(thisSE) > 0:
            pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, -unit * halfwidth, -(len(thisPairs) * 2 + 2) * unit * 2 + 2 * unit, unit * halfwidth, -(len(thisPairs) * 2 + 2) * unit * 2 + 2 * unit)

        # Differential Pairs

        ycnt = 0
        for pair in thisPairs:
            for i in [0, 1]:
                y = unit * (yMax + ycnt * 4 + (1 - i) * 2)
                pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B{5}\n'.format((pair[i][3] + '/' if pair[i][3] else '') + ('~' if i else '') + pair[i][1], ball_name[pair[i][9]] + str(pair[i][8]), x, y, part, ' C' if pair[i] in clk else '')
                
                #if pair[i][3]:
                #    pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, x - 160, y - 10, x - 160, y + 10)
            ycnt += 1

        ycnt = -1

        for pin in thisSE:
            y = unit * (yMax + ycnt * 2)
            pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B{5}\n'.format((pin[3] + '/' if pin[3] else '') + ('~' if i else '') + pin[1], ball_name[pin[9]] + str(pin[8]), x, y, part, ' C' if pin in clk else '')
                
                #if pair[i][3]:
                #    pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, x - 160, y - 10, x - 160, y + 10)
            ycnt -= 1
    

    #
    # Configuration
    #

    halfwidth = 12
    part += 1

    cfg.sort(key = lambda pin : pin[1])
    cfg = cfg[::-1]

    x = (3 + halfwidth) * unit
    yMax = 2 * -len(cfg) - 1

    pinStr += 'S {0} {1} {2} {3} {4} 1 0 f\n'.format(-unit * halfwidth, -(len(cfg) + 1) * unit * 2, unit * halfwidth, 0, part)
    pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -unit, part, '"Configuration (Bank 8)"')

    ycnt = 0
    for pin in cfg:
        y = unit * (yMax + ycnt * 2)
        pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B{5}\n'.format((pin[3]+ '/' if pin[3] else '') + pin[1], ball_name[pin[9]] + str(pin[8]), x, y, part, ' C' if pin in clk else '')

        ycnt += 1
    

    #
    # JTAG
    #

    halfwidth = 4
    part += 1

    cfg.sort(key = lambda pin : pin[1])
    cfg = cfg[::-1]

    x = (3 + halfwidth) * unit
    yMax = 2 * -len(jtag) - 1

    pinStr += 'S {0} {1} {2} {3} {4} 1 0 f\n'.format(-unit * halfwidth, -(len(jtag) + 1) * unit * 2, unit * halfwidth, 0, part)
    pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -unit, part, 'JTAG')

    ycnt = 0
    for pin in jtag:
        y = unit * (yMax + ycnt * 2)
        pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B{5}\n'.format((pin[3]+ '/' if pin[3] else '') + pin[1], ball_name[pin[9]] + str(pin[8]), x, y, part, ' C' if pin in clk else '')

        ycnt += 1
    

    #
    # SERDES
    #

    halfwidth = 6
    if len(serdesRX) > 0:
        #serdesRX.sort(key = lambda pin : pin[1])
        #serdesTX.sort(key = lambda pin : pin[1])
        #refclk  .sort(key = lambda pin : pin[1])
        num = 2 if len(serdesRX) == 8 else 1

        for i in range(num):
            part += 1
            x = (3 + halfwidth) * unit
            yMax = 2 * -len(jtag) - 1

            pinStr += 'S {0} {1} {2} {3} {4} 1 0 f\n'.format(-unit * halfwidth, -14 * unit, unit * halfwidth, 0, part)
            pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -unit, part, '"SERDES DCU' + str(i) + '"')

            pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, -unit * halfwidth,  -2 * unit, unit * halfwidth,  -2 * unit)
            pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, -unit * halfwidth,  -6 * unit, unit * halfwidth,  -6 * unit)
            pinStr += 'P 2 {0} 1 0 {1} {2} {3} {4} N\n'.format(part, -unit * halfwidth, -10 * unit, unit * halfwidth, -10 * unit)

            pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -4 * unit, part, 'CH0')
            pinStr += 'T 0 {0} {1} 50 0 {2} 1 {3} Normal 0 C C\n'.format(0, -12 * unit, part, 'CH1')

            y = -3 * unit
            for pin in serdesRX[4 * i : 4 * i + 2]:
                pinStr += 'X {0} {1} {2} {3} 150 R 50 50 {4} 1 B\n'.format(('' if 'P' in pin[1] else '~') + 'RX', ball_name[pin[9]] + str(pin[8]), -x, y, part)
                y -= 2 * unit

            for pin in refclk[2 * i : 2 * i + 2]:
                pinStr += 'X {0} {1} {2} {3} 150 R 50 50 {4} 1 B C\n'.format(('' if 'P' in pin[1] else '~') + 'CLK', ball_name[pin[9]] + str(pin[8]), -x, y, part)
                y -= 2 * unit

            for pin in serdesRX[4 * i + 2 : 4 * i + 4]:
                pinStr += 'X {0} {1} {2} {3} 150 R 50 50 {4} 1 B\n'.format(('' if 'P' in pin[1] else '~') + 'RX', ball_name[pin[9]] + str(pin[8]), -x, y, part)
                y -= 2 * unit

            y = -3 * unit
            for pin in serdesTX[4 * i : 4 * i + 2]:
                pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B\n'.format(('' if 'P' in pin[1] else '~') + 'TX', ball_name[pin[9]] + str(pin[8]), x, y, part)
                y -= 2 * unit

            y -= 4 * unit

            for pin in serdesTX[4 * i + 2 : 4 * i + 4]:
                pinStr += 'X {0} {1} {2} {3} 150 L 50 50 {4} 1 B\n'.format(('' if 'P' in pin[1] else '~') + 'TX', ball_name[pin[9]] + str(pin[8]), x, y, part)
                y -= 2 * unit
    
    deviceString = [s + '\n' for s in template.format(name = device_name, units = part, pins = pinStr, footprint = package).split('\n')]

    with open(kicadLibFile, 'r') as libFile:
        libString = libFile.readlines()

        insert = False
        startIndex = -1
        endIndex   = -1

        for i in range(len(libString)):
            if libString[i].startswith('DEF ' + device_name + ' '):
                insert = True
                startIndex = i

            if insert and startIndex != -1 and endIndex == -1 and libString[i].startswith('ENDDEF'):
                endIndex = i
        
        if insert:
            start = libString[0:startIndex]
            end = libString[endIndex + 1:-1]
            libString = start + deviceString + end
        else:
            libString.extend(deviceString)
        
    with open(kicadLibFile, 'w') as libFile:
        libFile.writelines(libString, )
