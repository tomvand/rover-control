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
        if 'delta_e' in log['VISUALHOMING_INS_CORRECTION']:
            # Old version
            # Collect EN position for plotting
            e = log['VISUALHOMING_STATE']['ins_e']
            n = log['VISUALHOMING_STATE']['ins_n']
            t = log['VISUALHOMING_STATE']['_time']
            # Plot INS corrections
            for i in range(len(log['VISUALHOMING_INS_CORRECTION']['_time'])):
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
        else:
            for i in range(len(log['VISUALHOMING_INS_CORRECTION']['_time'])):
                e_from = log['VISUALHOMING_INS_CORRECTION']['e_from'][i]
                n_from = log['VISUALHOMING_INS_CORRECTION']['n_from'][i]
                e_to = log['VISUALHOMING_INS_CORRECTION']['e_to'][i]
                n_to = log['VISUALHOMING_INS_CORRECTION']['n_to'][i]
                de = e_to - e_from
                dn = n_to - n_from
                plt.arrow(e_from, n_from, de, dn, color='black',
                          width=1e-4,
                          length_includes_head=True,
                          head_width=0.05)
                psi_from = log['VISUALHOMING_INS_CORRECTION']['psi_from'][i]
                psi_to = log['VISUALHOMING_INS_CORRECTION']['psi_to'][i]
                psi = np.linspace(psi_from, psi_to, 20)
                R = 0.10
                plt.plot(e_to + R * np.sin(psi), n_to + R * np.cos(psi), 'k')

    def plot_map(log):
        snapshot = {}
        odometry = {}
        for i in range(len(log['VISUALHOMING_MAP_TEL']['_time'])):
            snapshot_index = log['VISUALHOMING_MAP_TEL']['snapshot_index'][i]
            snapshot_e = log['VISUALHOMING_MAP_TEL']['snapshot_e'][i]
            snapshot_n = log['VISUALHOMING_MAP_TEL']['snapshot_n'][i]
            odometry_index = log['VISUALHOMING_MAP_TEL']['odometry_index'][i]
            odometry_e = log['VISUALHOMING_MAP_TEL']['odometry_e'][i]
            odometry_n = log['VISUALHOMING_MAP_TEL']['odometry_n'][i]
            snapshot[snapshot_index] = {'e': snapshot_e, 'n': snapshot_n}
            odometry[odometry_index] = {'e': odometry_e, 'n': odometry_n}
        for index, ss in snapshot.items():
            plt.plot(ss['e'], ss['n'], 'bo', markersize=10)
        for index, odo in odometry.items():
            plt.plot(odo['e'], odo['n'], 'rx', markersize=10)


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
    try: plot_map(log)
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
