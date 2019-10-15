#!/usr/bin/env python3

import binascii
import datetime
import json
import os
import requests
import shutil
import socket
import subprocess
import time


configuration_path = '/configuration.json'
proxy_list_path = '/server/proxy.conf'
secret_path = '/server/secret'


def download(path: str, source_url: str) -> bool:
    download_request = requests.get(source_url, stream=True)
    if download_request.status_code == 200:
        with open(path, 'wb') as output_file:
            download_request.raw.decode_content = True
            shutil.copyfileobj(download_request.raw, output_file)
        print('Download to {}: {}b'.format(path, os.path.getsize(path)))
        return True
    else:
        print('Download to {} failed: {}'.format(path, download_request.text))
        return False


def update_remote_configurations(retry_minutes: int) -> bool:
    print('Downloading remote configuration...')
    while True:
        updates_downloaded = False
        try:
            updates_downloaded = \
                download(secret_path, 'https://core.telegram.org/getProxySecret') and \
                download(proxy_list_path, 'https://core.telegram.org/getProxyConfig')
        except Exception as e:
            print('Download failed with an exception: {}'.format(e))

        if updates_downloaded:
            return True

        print('Retrying download in {} minutes.'.format(retry_minutes))
        time.sleep(60 * retry_minutes)


# Read configuration, if any.
with open(configuration_path) as configuration_file:
    configuration = json.load(configuration_file)

# Define proxy server parameters.
keys = configuration.get('keys', [])
new_keys = configuration.get('new_keys', 1)
update_hours = configuration.get('update_hours', 12)
ip = configuration.get('ip', '')
url = configuration.get('url', ip)
webport = configuration.get('webport', 80)
port = configuration.get('port', 443)
faketlsdomain = configuration.get('faketlsdomain', '')
tag = configuration.get('tag', '')

# Base command for mtproxy binary, with system user, stat and proxy ports.
command = '/server/mtproto-proxy -u nobody -p {} -H {}'.format(webport, port)
if tag:
    command += ' -P {}'.format(tag)
# Add Fake-TLS Domain
if faketlsdomain:
    command += ' -D {}'.format(faketlsdomain)

# Generate and print client keys.
for i in range(0, new_keys):
    keys.append(binascii.b2a_hex(os.urandom(16)).decode('UTF-8'))

# Print client keys with invite keys.
if not url:
    print('Warning! No server url or ip has been provided. Invite links will not be generated.')
for key in keys:
    print('>>>>>>>>>>')
    print('Key: {}'.format(key))
    if url:
        print('Link: tg://proxy?server={}&port={}&secret={}'.format(url, port, key))
    print('<<<<<<<<<<')
    command += ' -S ' + key

# Check if server is behind NAT (external ip should be provided).
if ip:
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    test_socket.connect(("8.8.8.8", 80))  # Use Google DNS as remote node.
    local_ip = test_socket.getsockname()[0]
    test_socket.close()
    if local_ip != ip:
        print('Server local and external IP mismatch: {} vs {}'.format(local_ip, ip))
        command += ' --nat-info {}:{}'.format(local_ip, ip)

# Configuration files.
command += ' --aes-pwd {} {}'.format(secret_path, proxy_list_path)

# Add Workers Parameter only if not in Fake-TLS Mode
if not faketlsdomain:
    command += ' -M 1'

# Write actual configuration values into local configuration.
configuration['keys'] = keys
configuration['new_keys'] = 0
configuration['update_hours'] = update_hours
configuration['ip'] = ip
configuration['url'] = url
configuration['webport'] = webport
configuration['port'] = port
configuration['faketlsdomain']=faketlsdomain
configuration['tag'] = tag
with open(configuration_path, 'w') as configuration_file:
    json.dump(configuration, configuration_file, indent='  ')
print('Configuration file updated: {}b'.format(os.path.getsize(configuration_path)))

# On first update, we should get configurations as fast, as possible.
update_remote_configurations(2)

# Outer loop: each iteration updates remote configuration and run server for |update_hours|
while True:
    start_time = time.time()
    # Inner loop: running and restarting the server, if it has crashed until the update time.
    while True:
        try:
            time_left = int(update_hours * 3600 - (time.time() - start_time))
            print('Launching at {}:\n{}'.format(datetime.datetime.now(), command))
            print('Server will be interrupted after {}'.format(datetime.timedelta(seconds=time_left)))
            print('------------------------------------------------------')
            server_process = subprocess.Popen(command.split())
            server_process.wait(timeout=time_left)
            # If we hit this, process has been terminated earlier than necessary. We should restart waiting cycle.
            print('------------------------------------------------------')
            print('Warning! Server exited unexpectedly with code {}'.format(server_process.returncode))
            continue
        except subprocess.TimeoutExpired:
            update_remote_configurations(30)
            print('Stopping server process for update')
            server_process.terminate()
            try:
                server_process.wait(timeout=20)
            except subprocess.TimeoutExpired:
                print('Warning! Server termination failed. Attempting to kill')
                server_process.kill()
                server_process.wait()
            print('------------------------------------------------------')
            break
