import re
import json

def log_to_signals(f):
    log = {}
    for line in f:
        m = re.match(r'(?P<time>[0-9.]+):(?P<data>{.+})', line)
        time = float(m.group('time'))
        data = json.loads(m.group('data'))
        data['_time'] = time

        msg = data['msgname']
        del(data['msgname'])
        del(data['msgclass'])
        if msg not in log:
            log[msg] = {}
        for key, value in data.items():
            if key not in log[msg]:
                log[msg][key] = []
            try:
                value = float(value)
            except:
                pass
            log[msg][key].append(value)
    return log


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    with open(args.filename, 'rt') as f:
        log = log_to_signals(f)

    print(json.dumps(log, indent=2))


    plt.figure()
    plt.plot(
        log['VISUALHOMING_STATE']['ins_e'],
        log['VISUALHOMING_STATE']['ins_n'],
        '-o'
    )
    plt.axis('equal')
    plt.grid(True)
    plt.show()
