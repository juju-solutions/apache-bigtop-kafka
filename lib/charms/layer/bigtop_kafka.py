import os
from charmhelpers.core import hookenv
from charmhelpers.core import host
from jujubigdata import utils
from charms.layer.apache_bigtop_base import Bigtop
from charms import layer


class Kafka(object):
    def __init__(self, dist_config=None):
        self.dist_config = dist_config or utils.DistConfig(data=layer.options('apache-bigtop-base'))

    def open_ports(self):
        for port in self.dist_config.exposed_ports('kafka'):
            hookenv.open_port(port)

    def configure_kafka(self, zk_units):
        # Get ip:port data from our connected zookeepers
        zks = []
        for unit in zk_units:
            ip = utils.resolve_private_address(unit['host'])
            zks.append("%s:%s" % (ip, unit['port']))
        zks.sort()
        zk_connect = ",".join(zks)
        service, unit_num = os.environ['JUJU_UNIT_NAME'].split('/', 1)
        kafka_port = self.dist_config.port('kafka')

        roles = ['kafka-server']
        override = {
            'kafka::server::broker_id': unit_num,
            'kafka::server::port': kafka_port,
            'kafka::server::zookeeper_connection_string': zk_connect,
        }

        bigtop = Bigtop()
        bigtop.render_site_yaml(roles=roles, overrides=override)
        bigtop.trigger_puppet()

    def restart(self):
        self.stop()
        self.start()

    def start(self):
        host.service_start('kafka-server')

    def stop(self):
        host.service_stop('kafka-server')
