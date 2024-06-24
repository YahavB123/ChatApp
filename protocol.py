import time

# fields sizes (in bytes)
LENGTH_FIELD_SIZE = 4
CMD_FIELD_SIZE = 1

# cmds
SET_NAME = 0
SEND_MSG = 1
EXIT = 2

PARAM_NUM = {SET_NAME: 1, SEND_MSG: 1, EXIT:0}


def create_client_msg(cmd, *params):
    if PARAM_NUM[cmd] != len(params):
        return None
    try:
        msg = f'{cmd:01}'
        for i in params:
            msg += f'{len(i):04}{i}'
        return msg

    except:
        return None


def create_server_msg(data):
    return f'{len(data):04}{data}'


def valid_username(username):
    if 0 < len(username) < 10000:
       return True
if __name__ == '__main__':
    print(create_client_msg(2))