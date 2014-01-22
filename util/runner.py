from subprocess import Popen
import os
import sys

ws_root = os.path.dirname(__file__) + '/../ws'
python_cmd = sys.executable

os.environ['PAGELIB_WS_IAM_CONFIG'] = ws_root + '/iam/config.py'
os.environ['PAGELIB_WS_INVOICING_CONFIG'] = ws_root + '/invoicing/config.py'

devnull = open('/dev/null', 'w')

iam_proc = Popen([python_cmd, ws_root + '/iam/app.py'],
                 stdout=devnull, stderr=devnull)

print 'IAM running (pid {})'.format(iam_proc.pid)

invoicing_proc = Popen([python_cmd, ws_root + '/invoicing/app.py'],
                       stdout=devnull, stderr=devnull)

print 'Invoicing running (pid {})'.format(invoicing_proc.pid)

try:
    while True:
        pass

except KeyboardInterrupt:
    iam_proc.terminate()
    invoicing_proc.terminate()
    print 'Killed processes'
