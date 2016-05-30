from charmhelpers.core import hookenv
from charms.layer.bigtop_kafka import Kafka
from charms.reactive import set_state, remove_state, when, when_not
from jujubigdata.utils import DistConfig
from charms.reactive.helpers import data_changed


@when('bigtop.available')
@when_not('zookeeper.joined')
def waiting_for_zookeeper():
    hookenv.status_set('blocked', 'Waiting for relation to Zookeeper')


@when('bigtop.available', 'zookeeper.joined')
@when_not('kafka.started', 'zookeeper.ready')
def waiting_for_zookeeper_ready(zk):
    hookenv.status_set('waiting', 'Waiting for Zookeeper to become ready')


@when('bigtop.available', 'zookeeper.ready')
@when_not('kafka.started')
def configure_kafka(zk):
    hookenv.status_set('maintenance', 'Setting up Kafka')
    kafka = Kafka()
    zks = zk.zookeepers()
    kafka.configure_kafka(zks)
    set_state('kafka.started')
    hookenv.status_set('active', 'Ready')


@when('kafka.started', 'zookeeper.ready')
def configure_kafka_zookeepers(zk):
    """Configure ready zookeepers and restart kafka if needed.

    As zks come and go, server.properties will be updated. When that file
    changes, restart Kafka and set appropriate status messages.
    """
    zks = zk.zookeepers()
    if not data_changed('zookeepers', zks):
        return

    hookenv.log('Checking Zookeeper configuration')
    kafka = Kafka()
    kafka.configure_kafka(zks)
    hookenv.status_set('active', 'Ready')


@when('kafka.started')
@when_not('zookeeper.ready')
def stop_kafka_waiting_for_zookeeper_ready():
    hookenv.status_set('maintenance', 'Zookeeper not ready, stopping Kafka')
    kafka = Kafka()
    kafka.stop()
    remove_state('kafka.started')
    hookenv.status_set('waiting', 'Waiting for Zookeeper to become ready')


@when('client.joined', 'zookeeper.ready')
def serve_client(client, zookeeper):
    kafka_port = DistConfig().port('kafka')
    client.send_port(kafka_port)
    client.send_zookeepers(zookeeper.zookeepers())
    hookenv.log('Sent Kafka configuration to client')
