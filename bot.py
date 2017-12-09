from shinobu.client import ShinobuClient

shinobu = ShinobuClient("shinobu.json")

token = shinobu.config['discord']['token']
shinobu.run(token)