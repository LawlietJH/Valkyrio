from src import Utils, Settings, Stranger
import _thread as thread
import _pickle as pickle
import atexit
import random
import socket
import json
import math
import time


# ======================================================================
# CLASSES ==============================================================
# ======================================================================

class Chat():
    def __init__(self):
        self.messages = {
            'global': []
        }
        self.qty_limit = 20

    def add(self, chat_type, username, msg):
        self.messages[chat_type].append((username, msg))

    def limit(self):
        if len(self.messages['global']) > self.qty_limit:
            self.messages['global'].pop(0)

#----------------

utils = Utils()
config = Settings(utils, is_client=False)
chat = Chat()

# ======================================================================
# FUNCTIONS ============================================================
# ======================================================================

def threaded_bot(stranger_id: int, stranger_name: str, level_min: int = 1, level_max: int = 10):
    global connections, players, game_time, _id #, current_levels

    if level_min < 1: level_min = 1

    # while True:
    #     r = random.randrange(1,224)

    #     if stranger_name == 'Iken':
    #         if     0 <= r <=  28: s_type = 5
    #         elif  28 <  r <=  56: s_type = 4
    #         elif  56 <  r <=  84: s_type = 3
    #         elif  84 <  r <= 112: s_type = 2
    #         elif 112 <  r:        s_type = 1

    #     current_levels[stranger_name].append(r)

    while True:
        # stranger_info = config.STRANGERS[stranger_name]

        r = random.randrange(level_min, level_max+1)
        stranger_info = config.getStranger(stranger_name, r)

        map_limits = config.MAP[config.map_name]

        players[stranger_id] = {
            'x':     random.randrange(20*config.posdiv, (map_limits['x']-20)*config.posdiv),
            'y':     random.randrange(20*config.posdiv, (map_limits['y']-20)*config.posdiv),
            'name':  f'{stranger_name} {stranger_info["type"]}',        # Stranger name and type
            'type':  'Stranger',                                        # Type of ship
            'creds': stranger_info['creds'],                            # Number of credits
            'exp':   stranger_info['exp'],                                # Score
            'ang':   0,                                                    # Angle
            'atk':   False,                                                # Attacking
            'ship': {
                'name':    stranger_name,                                # Ship Name
                'path':    stranger_info['path'],                        # Path of ship design
                'level':     stranger_info['level'],                        # Stranger level
                'lhp':     stranger_info['lhp'],                        # Health Points
                'lsp':     stranger_info['lsp'],                        # Shield Points
                'chp':     stranger_info['lhp']*stranger_info['hp'],    # Current Health Points
                'csp':     stranger_info['lsp']*stranger_info['sp'],    # Current Shield Points
                's_unlkd': True,                                        # Shield Unlocked
                'dtry':    False,                                        # Destroyed
                'spd_level': stranger_info['spd_level'],                    # Speed level
                'weapon': {
                    'name': stranger_info['wpn_name'],                    # Weapon name
                    'level':  stranger_info['wpn_level']                    # Weapon level
                }
            },
            'selected': {
                'name': '',                                                # Selected Username
                'id':   -1,                                                # Selected ID user
            },
            'dmginfo': {}
        }

        stranger = Stranger(config, players[stranger_id], stranger_id)
        stranger.loadData(players)

        print(f"[LOG] {stranger_name} ({stranger.ship.level}) Generated. ID: {stranger_id} ({int(stranger.x/config.posdiv)},{int(stranger.y/config.posdiv)})")

        deltaTime = 1

        # TODO: Hacer opaco cuando es destruido
        while stranger.ship.chp > 0:
            try:
                game_time = int(time.perf_counter()-start_time)

                stranger.chkDmgRecv(players)
                stranger.setData(players)
                stranger.ship.healHP()
                stranger.ship.healSP()
                stranger.radioactiveZone()
                stranger.randomMove(players, game_time, FPS)

                deltaTime = stranger.deltaTime(FPS) / config.dtdiv

            except Exception as e:
                # [DISCONNECT] Name: xD, Client Id: 96 disconnected
                # Exception ignored in thread started by: <function threaded_bot at 0x000001A2EE59FD30>
                # Traceback (most recent call last):
                #   File "Server.py", line 919, in threaded_bot
                #     stranger.setData()
                #   File "Server.py", line 506, in setData
                #     dmginfo = players[data['dmginfo']['id']]['dmginfo']
                # KeyError: 96
                if not str(e).startswith('[WinError 10054]'):
                    print(e, 'Error')
                break

        print(f'[LOG] Destroyed: {stranger_name}, ID: {stranger_id}')

        try:
            players[stranger.primary_atk]['creds'] += players[stranger_id]['creds']
            players[stranger.primary_atk]['exp']   += players[stranger_id]['exp']
        except: pass

        time.sleep(3)

        del players[stranger_id]

        _id += 1
        stranger_id = _id

def threaded_client(conn, _id):
    global connections, players, game_time, start

    current_id = _id
    map_limits = config.MAP[config.map_name]

    data = conn.recv(24)
    name = data.decode('utf-8')
    print(f"[LOG] '{name}' connected to the server. Client Id: {_id}")

    players[current_id] = {
        'x':     random.randrange(20*config.posdiv, (map_limits['x']-20)*config.posdiv),
        'y':     random.randrange(20*config.posdiv, (map_limits['y']-20)*config.posdiv),
        'name':  name,                    # Username
        'type':  'Human',                # Type of ship
        'creds': 0,                        # Number of credits
        'exp':   0,                        # Score
        'ang':   0,                        # Angle
        'atk':   False,                    # Attacking
        'ship': {
            'level':     0,
            'name':    'Prometheus',    # Ship Name
            'lhp':     20,                # Health Points
            'lsp':     20,                # Shield Points
            'chp':     0,                # Current Health Points
            'csp':     0,                # Current Shield Points
            's_unlkd': True,            # Shield Unlocked
            'dtry':    False,            # Destroyed
            'spd_level': 0,                # Speed
            'weapon': {
                'name': 'Laser',        # Weapon name
                'level': 0                # Weapon level
            }
        },
        'selected': {
            'name': '',                    # Selected Username
            'id':   -1,                    # Selected ID user
        },
        'dmginfo': {}
    }

    conn.send(str.encode(str(current_id)))

    while True:
        try:
            game_time = int(time.perf_counter()-start_time)

            data = conn.recv(kbyte)

            if not data: break

            data = data.decode('utf-8')
            #print('[DATA] Recieved', data, 'from client id:', current_id)

            if data.startswith('data:'):
                data = data[len('data:'):]
                data = json.loads(data)

                player = players[current_id]
                player_s = player['ship']
                player_sw = player_s['weapon']

                data_s = data['shipdata']
                data_sw = data_s['weapon']

                if not player['x']         == data['x']:                     player['x']         = data['x']
                if not player['y']         == data['y']:                     player['y']         = data['y']
                if not player['creds']     == data['creds']:                 player['creds']     = data['creds']
                if not player['exp']       == data['exp']:                   player['exp']       = data['exp']
                if not player['ang']       == data['ang']:                   player['ang']       = data['ang']
                if not player['atk']       == (data['atk'] == 'True'):       player['atk']       = data['atk'] == 'True'
                if not player_s['name']    == data_s['name']:                player_s['name']    = data_s['name']
                if not player_s['lhp']     == data_s['lhp']:                 player_s['lhp']     = data_s['lhp']
                if not player_s['lsp']     == data_s['lsp']:                 player_s['lsp']     = data_s['lsp']
                if not player_s['chp']     == data_s['chp']:                 player_s['chp']     = data_s['chp']
                if not player_s['csp']     == data_s['csp']:                 player_s['csp']     = data_s['csp']
                if not player_s['s_unlkd'] == (data_s['s_unlkd'] == 'True'): player_s['s_unlkd'] = data_s['s_unlkd'] == 'True'
                if not player_s['dtry']    == (data_s['dtry'] == 'True'):    player_s['dtry']    = data_s['dtry'] == 'True'
                if not player_s['spd_level'] == data_s['spd_level']:             player_s['spd_level'] = data_s['spd_level']
                if not player_sw['name']   == data_sw['name']:               player_sw['name']   = data_sw['name']
                if not player_sw['level']    == data_sw['level']:                player_sw['level']    = data_sw['level']

                if data['dmginfo']['dmg'] > 0 and data['dmginfo']['id'] >= 0:

                    dmginfo = players[data['dmginfo']['id']]['dmginfo']

                    if not dmginfo.get(current_id):
                        dmginfo[current_id] = []

                    dmginfo[current_id].append([
                        data['dmginfo']['dmg'],
                        data['dmginfo']['pct_sp'],
                        data['dmginfo']['mult'],
                        data['dmginfo']['time']
                    ])

                send_data = pickle.dumps((players, game_time))

                # for id_, dmginfo in players[current_id]['dmginfo'].items():
                #     for di in dmginfo:
                #         print(di[3])

                players[current_id]['dmginfo'] = {}

            elif data.startswith('id'):
                send_data = str.encode(str(current_id))

            elif data.startswith('selected:'):
                data = data[len('selected:'):]
                data = json.loads(data)
                selected_name = data['name']
                selected_id   = data['id']
                name = players[current_id]['name']

                if not selected_name:
                    unselected = players[current_id]['selected']['name']
                    print(f"[UNSELECT] '{name}' (ID:{current_id}) unselect to '{unselected}' (ID:{players[current_id]['selected']['id']})")
                else:
                    print(f"[SELECT] '{name}' (ID:{current_id}) select to '{selected_name}' (ID:{selected_id})")

                players[current_id]['selected']['name'] = selected_name
                if selected_name:
                    players[current_id]['selected']['id'] = int(selected_id)
                else:
                    players[current_id]['selected']['id'] = -1

                send_data = pickle.dumps(players)

            elif data.startswith('msg:'):
                msg = data[len('msg:'):]
                data = msg.split(':')
                chat_type = data[0]
                username  = data[1]
                msg = ':'.join(data[2:])
                chat.add(chat_type, username, msg)
                chat.limit()
                send_data = pickle.dumps(chat.messages)

            elif data == 'get msg':
                send_data = pickle.dumps(chat.messages)

            elif data == 'get':
                send_data = pickle.dumps(players)

            else: send_data = pickle.dumps((players, game_time))

            conn.send(send_data)

        except Exception as e:
            print(e)
            # if not str(e).startswith('[WinError 10054]'):
                # print(e, 'Error')
            break

        time.sleep(1/FPS)

    print(f'[DISCONNECT] Name: {name}, Client Id: {current_id} disconnected')

    connections -= 1
    del players[current_id]
    conn.close()

def generateStranger(stranger_name, r_min, r_max):
    global _id
    _id += 1
    thread.start_new_thread(threaded_bot, (_id, stranger_name, r_min, r_max))
    time.sleep(.01)

@atexit.register
def close():
    time.sleep(1)

# ======================================================================
# ======================================================================
# ======================================================================

# setup sockets
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Set constants
PORT = 57575
HOST_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(HOST_NAME)
FPS = 240

# try to connect to server
try:
    # S.bind((SERVER_IP, PORT))
    S.bind(('127.0.0.1', PORT))
except socket.error as e:
    print(str(e))
    print('[SERVER] Server could not start')
    quit()

# listen for connections
S.listen()

print(f'[SERVER] Server Started with local ip {SERVER_IP}')

# dynamic variables
players = {}
connections = 0
_id = -1
start = False
start_time = 0
game_time = 'Starting Soon'
kbyte = 1024

current_levels = {
    'Iken': []
}

# STRANGERS ============================================================

for i in range(20):
    i+=1
    if i <= 20:
        generateStranger('Iken',  1, 12)
    elif i <= 24:
        generateStranger('Iken', 13, 24)
    elif i <= 26:
        generateStranger('Iken', 25, 27)
    elif i == 27:
        generateStranger('Iken', 28, 55)
    elif i == 28:
        generateStranger('Iken', 56, 84)
    elif i == 29:
        generateStranger('Iken', 85, 111)
    else:
        generateStranger('Iken', 112, 120)

# MAINLOOP =============================================================

print('[GAME] Setting up level')
print('[SERVER] Waiting for connections')

while True:
    host, addr = S.accept()
    print(f'[CONNECTION] Connected to: {addr}')

    if addr[0] == SERVER_IP and not(start):
        start = True
        start_time = time.perf_counter()
        print('[STARTED] Game Started')

    _id += 1
    connections += 1
    thread.start_new_thread(threaded_client,(host,_id))

print('[SERVER] Server offline')

#TODO: Implementar atajo para cerrar el servidor
