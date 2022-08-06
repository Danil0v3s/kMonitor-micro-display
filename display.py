import gc

gc.collect()

from writer import Writer
from machine import Pin, I2C
import font6, freesans20
import sh1106_i2c as sh

gc.collect()

ssd = sh.SH1106(128,64,I2C(sda=Pin(4), scl=Pin(5)))
smallFont = Writer(ssd,font6,verbose=False)
bigFont = Writer(ssd,freesans20,verbose=False)
gc.collect()
ssd.fill(0)
ssd.show()

def showCPU(temp, usage):
    Writer.set_textpos(ssd,0,0)
    smallFont.printstring('CPU ')
    bigFont.printstring('{}C '.format(temp))
    Writer.set_textpos(ssd,row=5,col=None)
    smallFont.printstring('{}% '.format(usage))
    ssd.show()


def showGPU(temp, usage):
    Writer.set_textpos(ssd,20,0)
    smallFont.printstring('GPU ')
    bigFont.printstring('{}C '.format(temp))
    Writer.set_textpos(ssd,row=25,col=None)
    smallFont.printstring('{}%'.format(usage))
    ssd.show()

def showFPS(frames, time):
    Writer.set_textpos(ssd,40,0)
    smallFont.printstring('FPS ')
    bigFont.printstring('{} '.format(frames))
    Writer.set_textpos(ssd,row=45,col=None)
    smallFont.printstring('{}ms'.format(time))
    ssd.show()

async def main():
    import json
    gc.collect()
    import uwebsockets.socketclient as client
    async with await client.connect("ws://192.168.1.208:8080/socket?slim=true&filter=MONITORING_SOURCE_ID_GPU_USAGE,MONITORING_SOURCE_ID_GPU_TEMPERATURE,MONITORING_SOURCE_ID_CPU_TEMPERATURE,MONITORING_SOURCE_ID_CPU_USAGE") as websocket:
        while True:
            entries = json.loads(await websocket.recv())['entries']
            gpu_temp = [x for x in entries if x.dwSrcId == "MONITORING_SOURCE_ID_GPU_TEMPERATURE"][0]
            print(gpu_temp)
            gc.collect()

def start():
    gc.collect()
    import uasyncio
    loop = uasyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()