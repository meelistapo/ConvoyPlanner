import sys
import zerorpc
import gevent
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
            return calculate(data)
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
    gevent.spawn(s.run())


if __name__ == '__main__':
    main()
