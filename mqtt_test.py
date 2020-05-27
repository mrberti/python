import paho.mqtt.client as mqtt
import time
import ssl

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("test/#")
    # client.subscribe("$SYS/#")
    client.publish("test/connect", "MQTT connected", retain=True)

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

# client = mqtt.Client(client_id="mqtt-keezer", clean_session=False)
client = mqtt.Client()

# client.tls_set("letsencrypt.crt")
# client.tls_set(
#     ca_certs="ca_bundle.crt",
#     # certfile="certificate.crt",
#     # keyfile="private.key",
#     # ciphers="ECDHE-RSA-AES256-GCM-SHA384",
#     tls_version=5,
#     )
# client.tls_insecure_set(True)

client.on_connect = on_connect
client.on_message = on_message
# client.username_pw_set("simon", "supipass")
# client.username_pw_set("keezer:keezer", "keezer")

# client.connect("iot.eclipse.org", 1883, 60)
client.connect("test.mosquitto.org")
# client.connect("m2m.eclipse.org", 1883, 60)
# client.connect("mrberti.ddns.net", 1883, 60)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.publish("test/connect", "MQTT disconnected", retain=True)
    client.disconnect()

