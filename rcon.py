from mcrcon import MCRcon
import config

mcr = MCRcon(host=config.rcon_host, port=config.rcon_port, password=config.rcon_password)
mcr.connect()

def addplayertowhitelist(nickname):
    mcr.connect()
    wlist = mcr.command(f"whitelist add {nickname}")
    mcr.disconnect()
    return wlist

def removeplayerfronwhitelist(nickname):
    mcr.connect()
    blist = mcr.command(f"whitelist remove {nickname}")
    mcr.disconnect()
    return blist

def getwhitelistlist():
    mcr.connect()
    whitelistlist = mcr.command(f"whitelist list")
    mcr.disconnect()
    return whitelistlist

mcr.disconnect()
