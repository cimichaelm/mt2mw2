# system library
import configparser as cp

# our library
from mindtouch import MTWiki
from mediawiki import MWWiki

cfg = cp.SafeConfigParser()
cfg.read('config.ini')

# get the root element in the page structure
print("Attempting to get the mindtouch wiki layout")
mtwiki = MTWiki(cfg.get('config', 'mindtouch_url'))
homepage = mtwiki.get_sitemap()
if homepage:
    print("Have mindtouch layout.")

directdb = cfg.get('config', 'direct_db')
dbconfig = None
flg_copyfiles = cfg.getboolean('config', 'copyfiles',fallback=True)
flg_copypages = cfg.getboolean('config', 'copypages',fallback=True)

if directdb:
    dbconfig = {
        'host': cfg.get('config', 'mediawiki_db_host'),
        'port': cfg.get('config', 'mediawiki_db_port'),
        'database': cfg.get('config', 'mediawiki_db'),
        'user': cfg.get('config', 'mediawiki_db_user'),
        'password': cfg.get('config', 'mediawiki_db_password'),
    }
    print("Will use DB connection")

print("Attempting to create mediawiki connection")
print("Copying files: {0}, Copying pages: {1}".format(flg_copyfiles, flg_copypages))

mwwiki = MWWiki(
    cfg.get('config', 'mediawiki_url'),
    cfg.get('config', 'mediawiki_user'),
    cfg.get('config', 'mediawiki_password'),
    dbconfig,
    cfg.get('config', 'dataroot'),
)
if mwwiki:
    print("MediaWiki Connection created")
    mwwiki.set_copyfiles(flg_copyfiles)
    mwwiki.set_copypages(flg_copypages)

print("Creating MediaWiki from mindtouch site...")
mwwiki.create_from_mindtouch(homepage)
print("MediaWiki updated")

# point MediaWiki:MainPage at the new homepage
print("Updating MediaWiki homepage")
mwwiki.update_mainpage(homepage)
mwwiki.done()
print("All done!")
