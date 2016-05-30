import re
import sys
import yaml

from charmhelpers.core import hookenv


def fail(msg, output='<No output>'):
    hookenv.action_set({'output': output})
    hookenv.action_fail(msg)
    sys.exit()


def get_zookeepers():
    cfg = '/etc/kafka/conf/server.properties'
    print(cfg)
    file = open(cfg, "r")

    for line in file:
        if re.search('^zookeeper.connect=.*', line):
            zks = line.split("=")[1].strip('\n')
            return zks

    return None
