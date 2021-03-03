import os
import sys
import re
import binascii

import grpc
from chirpstack_api.as_pb.external import api


textfile = open("test.txt", 'r')
filecontent = textfile.read()
textfile.close()
matches = re.search("DevEui:(.{16})", filecontent)
raw_dev_uid = matches.group(1)

matches = re.search("AppKey:(.{32})", filecontent)
raw_nwk_key = matches.group(1)

print("dev_EUI:" + raw_dev_uid)
print("nwk_key:" + raw_nwk_key)

dev_eui = bytes.fromhex(raw_dev_uid)
nwk_key = bytes.fromhex(raw_nwk_key)

application_id = 1 #1 = Testdevice; 3=CO2
device_profile_id = "da568541-4daa-4e07-be88-7a898177e5ee" # ERS device
description_prefix = "CO2-"
tags = {"building": "zuhause", "we": "12345"}


# Configuration.

# This must point to the API interface.
server = "192.168.101.191:8080"

app_key = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

# The API token (retrieved using the web-interface).
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGlfa2V5X2lkIjoiODI0MTljMjEtZTI4Yi00NGQ1LWJiYjUtYzRjY2FhMTU2OTQ4IiwiYXVkIjoiYXMiLCJpc3MiOiJhcyIsIm5iZiI6MTYxNDc2NDgxNywic3ViIjoiYXBpX2tleSJ9.zUeAXRh2Hk7kJ_UnXeUPmrsLb4KumgKiYy2N2ricMHg"

if __name__ == "__main__":
  # Connect without using TLS.
  channel = grpc.insecure_channel(server)

  # Device-queue API client.
  client = api.DeviceServiceStub(channel)

  # Define the API key meta-data.
  auth_token = [("authorization", "Bearer %s" % api_token)]

  # Construct request.
  req = api.CreateDeviceRequest()
  req.device.dev_eui = dev_eui.hex()
  req.device.name = raw_dev_uid
  req.device.application_id = application_id
  req.device.description = description_prefix + raw_dev_uid[8:]
  req.device.device_profile_id = device_profile_id
  req.device.is_disabled = False
  req.device.skip_f_cnt_check = True
  req.device.tags.update(tags)

  resp = client.Create(req, metadata=auth_token)

  print(resp)

  print("Device imported")
  
  req = api.CreateDeviceKeysRequest()
  req.device_keys.dev_eui = dev_eui.hex()
  req.device_keys.nwk_key = nwk_key.hex()
  req.device_keys.app_key = app_key.hex()

  resp = client.CreateKeys(req, metadata=auth_token)
  
  print(resp)
  
  print("Keys set")
  
  
  
  