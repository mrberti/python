# import paho.mqtt.client as mqtt
# import time
# import ssl

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code " + str(rc))
#     client.subscribe("test/#")
#     # client.subscribe("$SYS/#")
#     client.publish("test/connect", "MQTT connected", retain=True)

# def on_message(client, userdata, msg):
#     print(msg.topic + " " + str(msg.payload))

# # client = mqtt.Client(client_id="mqtt-keezer", clean_session=False)
# client = mqtt.Client()

# # client.tls_set("letsencrypt.crt")
# # client.tls_set(
# #     ca_certs="ca_bundle.crt",
# #     # certfile="certificate.crt",
# #     # keyfile="private.key",
# #     # ciphers="ECDHE-RSA-AES256-GCM-SHA384",
# #     tls_version=5,
# #     )
# # client.tls_insecure_set(True)

# client.on_connect = on_connect
# client.on_message = on_message
# # client.username_pw_set("simon", "supipass")
# # client.username_pw_set("keezer:keezer", "keezer")

# client.connect("iot.eclipse.org", 80, 60)
# # client.connect("test.mosquitto.org")
# # client.connect("m2m.eclipse.org", 1883, 60)
# # client.connect("mrberti.ddns.net", 1883, 60)

# try:
#     client.loop_forever()
# except KeyboardInterrupt:
#     client.publish("test/connect", "MQTT disconnected", retain=True)
#     client.disconnect()

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
