import sys
import zerorpc
import gevent
import traceback
from exact import calculate


class ConvoyApi(object):

    def calc(self, data):
        """based on the input text, return the int result"""
        try:
            # return real_calc(text)
            return calculate(data)
        except Exception as e:
            return 0.0

    def generatePaths(self, data):
        """based on the input text, return the int result"""
        try:
            # return '1 [164 3583 2960] 0.2580022264992 0|3 [1660 2557 704 813] 0.06120995327724 0|2 [3338 3583 3800] 0.43484810014 0.07506187486113335|'
            return calculate(data)
        except Exception as e:

            # return  traceback.print_exc()
            return  sys.exc_info()[0]
            # traceback.print_tb(e.__traceback__)
            # return e

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
    gevent.spawn(s.run())


if __name__ == '__main__':
    main()
