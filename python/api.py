import sys
import zerorpc
import gevent
import signal
from collection import collect



class ConvoyApi(object):

    def generatePaths(self, data):
        try:
            result = False
            while not result:
                gevent.sleep(1)
                result = collect(data)
            return result
        except Exception as e:
            return e

    def echo(self, text):
        """echo any text"""
        return text


def parse_port():
    port = 4242
    try:
        port = int(sys.argv[1])
    except Exception as e:
        pass
    return '{}'.format(port)


def main():
    addr = 'tcp://127.0.0.1:4242'
    s = zerorpc.Server(ConvoyApi())
    s.bind(addr)
    print('start running on {}'.format(addr))
    gevent.signal(signal.SIGTERM, s.stop)
    gevent.spawn(s.run())
    print("zpc stopped")
    sys.stdout.flush()


if __name__ == '__main__':
    main()
