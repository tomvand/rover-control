import re
import json

def log_to_signals(f):
    log = {}
    for line in f:
        m = re.match(r'(?P<time>[0-9.]+):(?P<data>{.+})', line)
        if m is not None:
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


try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    pass
else:
    def plot_colored(x, y, c, cmap=plt.cm.get_cmap('jet'), steps=10):
        # https://stackoverflow.com/a/54315981
        c = np.asarray(c)
        c -= np.min(c)
        c /= np.max(c)
        c2 = c  # Not sure why python needs this...
        it = 0
        while it < c2.size - steps:
            x_segm = x[it:it + steps + 1]
            y_segm = y[it:it + steps + 1]
            c_segm = cmap(c[it + steps // 2])
            plt.plot(x_segm, y_segm, c=c_segm)
            it += steps

    def plot_ins_pos(log):
        # plt.plot(
        #     log['VISUALHOMING_STATE']['ins_e'],
        #     log['VISUALHOMING_STATE']['ins_n'],
        #     '-'
        # )
        plot_colored(
            log['VISUALHOMING_STATE']['ins_e'],
            log['VISUALHOMING_STATE']['ins_n'],
            log['VISUALHOMING_STATE']['_time']
        )
        plt.axis('equal')
        plt.grid(True)

    def plot_ins_time(log):
        plt.subplot(3, 1, 1)
        plt.plot(log['VISUALHOMING_STATE']['_time'], log['VISUALHOMING_STATE']['ins_e'])
        plt.ylabel('E [m]')
        plt.subplot(3, 1, 2)
        plt.plot(log['VISUALHOMING_STATE']['_time'], log['VISUALHOMING_STATE']['ins_n'])
        plt.ylabel('N [m]')
        plt.subplot(3, 1, 3)
        plt.plot(log['VISUALHOMING_STATE']['_time'], np.rad2deg(np.unwrap(log['VISUALHOMING_STATE']['psi'])))
        plt.ylabel('Psi [deg]')

    def plot_vectors(log):
        for i in range(len(log['VISUALHOMING']['_time'])):
            x = log['VISUALHOMING']['from_e'][i]
            y = log['VISUALHOMING']['from_n'][i]
            dx = log['VISUALHOMING']['to_e'][i] - x
            dy = log['VISUALHOMING']['to_n'][i] - y
            color = 'red' if log['VISUALHOMING']['source'][i] == 1 else 'blue'
            plt.arrow(x, y, dx, dy, color=color,
                      width=1e-4,
                      alpha=0.3,
                      length_includes_head=True,
                      head_width=0.05)
        plt.axis('equal')
        plt.grid(True)

    def plot_vectors_yaw(log):
        plt.plot(log['VISUALHOMING']['_time'], np.rad2deg(log['VISUALHOMING']['delta_yaw']))
        plt.ylabel('Delta_psi [deg]')

    def plot_ins_correction(log):
        # Collect EN position for plotting
        e = log['VISUALHOMING_STATE']['ins_e']
        n = log['VISUALHOMING_STATE']['ins_n']
        t = log['VISUALHOMING_STATE']['_time']
        # Plot INS corrections
        for i in range(len(log['VISUALHOMING_INS_CORRECTION'])):
            tc = log['VISUALHOMING_INS_CORRECTION']['_time'][i]
            de = log['VISUALHOMING_INS_CORRECTION']['delta_e'][i]
            dn = log['VISUALHOMING_INS_CORRECTION']['delta_n'][i]
            dpsi = log['VISUALHOMING_INS_CORRECTION']['delta_psi'][i]
            efrom = np.interp(tc, t, e)
            nfrom = np.interp(tc, t, n)
            plt.arrow(efrom, nfrom, de, dn, color='black',
                      width=1e-4,
                      length_includes_head=True,
                      head_width=0.05)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()

    with open(args.filename, 'rt') as f:
        log = log_to_signals(f)

    print(json.dumps(log, indent=2))

    plt.figure()
    try: plot_vectors(log)
    except: pass
    try: plot_ins_pos(log)
    except: pass
    try: plot_ins_correction(log)
    except: pass

    plt.figure()
    try: plot_ins_time(log)
    except: pass

    plt.figure()
    try: plot_vectors_yaw(log)
    except: pass

    plt.show()
