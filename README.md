# MTProxy v1.1
Lightweight and easy to set up docker image for MTProto proxy server.

[![Docker Build Status](https://img.shields.io/docker/build/viers/mtproxy.svg)](https://hub.docker.com/r/viers/mtproxy/)
[![Docker Pulls](https://img.shields.io/docker/pulls/viers/mtproxy.svg)](https://hub.docker.com/r/viers/mtproxy/)
[![MicroBadger Size](https://images.microbadger.com/badges/image/viers/mtproxy.svg)](https://microbadger.com/images/viers/mtproxy)

Binary inside: [f9158e3129efd4c from 19 Jul 2018](https://github.com/TelegramMessenger/MTProxy/commit/f9158e3129efd4ccdc291aefb840209791226a77)

### How to run:
All you need is an installed docker. A server must be configured with the special json dictionary file, mounted as `/configuration.json`. To get configuration template, you may run a container with an empty configuration file (only `{}` inside).

After the configuration file is mounted, it will be modified from inside the container, so that generated data will be kept after restart. Changing this file on the host would not affect the container until the manual container restart.

Configuration parameters:

* `keys`: An array of client keys, if you have generated some before. By default, this array is empty. 
* `new_keys`: Number of new client keys to generate. If you have no existing keys, you should generate at least one. Default value: 1
* `update_hours`: How often telegram servers list will be updated. Default value: 12.
* `ip`: Server external IP. Necessary for servers behind NAT, also used in invite links, if server URL was not provided. By default is empty.
* `url`: Server URL, if any, to be used in invite links. Default value: same as `ip`.
* `webport`: Port for HTTP Stats. Default value: 80
* `port`: Exposed server port for invite links. Default value: 443.
* `faketlsdomain`: Fake-TLS Domain (MTproxy -D Parameter)
* `tag`: Your proxy tag, optionally received from [@MTProxyBot](https://t.me/MTProxybot). By default is empty.

To launch container: `docker run -d --restart always -p [server-port]:443 -v [full-configuration-file-path]:/configuration.json --name mtproxy viers/mtproxy`.

To see the logs: `docker logs --follow mtproxy`.

To collect server stats: `docker exec mtproxy curl http://localhost:80/stats`

Example Configuration:
{
  "keys": [
    ""
  ],
  "new_keys": 0,
  "update_hours": 12,
  "ip": "",
  "url": "",
  "webport": 80,
  "port": 443,
  "faketlsdomain": "",
  "tag": ""
}
