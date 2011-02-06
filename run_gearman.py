# run_gearman.py
# -*- encoding:utf-8 -*-

from flask import Flask
import ponyexpress

ponyexpress.app.config.from_envvar('PONYEXPRESS_CFG')
ponyexpress.couch.init(ponyexpress.app.config)
import ponyexpress.gearman_interface
ponyexpress.gearman_interface.config = ponyexpress.app.config
#import PonyExpressClient, config
ponyexpress.gearman_interface.PonyExpressClient.start_gearman([ponyexpress.app.config.get('gearman_servers','localhost:4730')])
