#!/usr/bin/env nix-shell
#!nix-shell -p "python3.withPackages(ps: with ps; [ requests pyyaml ])" -i python3

import io
import json
import requests
import tarfile
import yaml
import datetime

URL = "https://github.com/iamcal/oembed/archive/master.tar.gz"

r = requests.get(URL, allow_redirects=True)
fp = io.BytesIO(r.content)
fp.seek(0)

endpoints = []

tar = tarfile.open(fileobj=fp, mode="r:gz")
for info in tar:
    if all([
        info.isfile(),
        "providers" in info.path,
        info.path.endswith(".yml")
    ]):
        fb_ = tar.extractfile(info)
        data = yaml.safe_load(fb_)
        for provider in data:
            for e in provider['endpoints']:
                endpoints.append([
                    e['url'],
                    e.get('schemes', [provider['provider_url'] + '*'])
                ])

print(f"""\
\"\"\"oEmbed providers from https://github.com/iamcal/oembed\"\"\"
# {datetime.datetime.now().isoformat()}

PROVIDERS = {json.dumps(sorted(endpoints), indent=4)}
""")
