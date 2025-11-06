import signal
import sys

def register_sigint():
    def signal_handler(sig, frame):
        print('\n(SIGINT) quit')
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
