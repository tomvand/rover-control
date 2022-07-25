from types import SimpleNamespace
import numpy as np
from scipy.spatial.transform import Rotation as R

from copy import deepcopy


# Optitrack rottaion matrices
w_Rmat_o = np.array([[1,  0,  0],
                     [0,  0,  1],
                     [0, -1,  0]])  # Optitrack to world NED
rb_Rmat_d = np.array([[0,  1,  0],
                      [0,  0,  1],
                      [1,  0,  0]])  # Drone FRD to optitrack rigid body


def parse_optitrack_csv(fp):
    # Find start of data
    for line in fp:
        if line.startswith(',,Rotation'):
            break
    # Parse header
    header_cols = line.split(',')
    assert(all([c == 'Rotation' for c in header_cols[2:6]]))
    assert(all([c == 'Position' for c in header_cols[6:9]]))
    # Parse header 2
    for line in fp:
        assert(line.startswith('Frame,Time,X,Y,Z,W,X,Y,Z,'))
        break
    # Read rows
    ot = {
        'time': [],
        'rot_qx': [],
        'rot_qy': [],
        'rot_qz': [],
        'rot_qw': [],
        'rot_phi': [],
        'rot_theta': [],
        'rot_psi': [],
        'pos_x': [],
        'pos_y': [],
        'pos_z': [],
    }
    for row in fp:
        cols = row.split(',')
        ot['time'].append(float(cols[1]))
        ot['rot_qx'].append(float(cols[2]))
        ot['rot_qy'].append(float(cols[3]))
        ot['rot_qz'].append(float(cols[4]))
        ot['rot_qw'].append(float(cols[5]))
        ot['pos_x'].append(float(cols[6]))
        ot['pos_y'].append(float(cols[7]))
        ot['pos_z'].append(float(cols[8]))

        rot_qx, rot_qy, rot_qz, rot_qw = float(cols[2]), float(cols[3]), float(cols[4]), float(cols[5])
        o_quat_rb = R.from_quat([rot_qx, rot_qy, rot_qz, rot_qw])
        o_Rmat_rb = o_quat_rb.as_matrix()
        w_Rmat_d = w_Rmat_o @ o_Rmat_rb @ rb_Rmat_d
        psi = np.arctan2(w_Rmat_d[1, 0], w_Rmat_d[0, 0])
        theta = np.arctan2(-w_Rmat_d[2, 0], np.sqrt(w_Rmat_d[1, 0]**2 + w_Rmat_d[0, 0]**2))
        euler = R.from_matrix(w_Rmat_d).as_euler('zxy')  # TODO verify exact axis configuration
        ot['rot_phi'].append(0)
        ot['rot_theta'].append(theta)
        ot['rot_psi'].append(psi)
    ot['pos_e'] = ot['pos_z']
    ot['pos_n'] = ot['pos_x']
    ot['pos_u'] = ot['pos_y']
    return SimpleNamespace(**ot)


def clean_optitrack(ot_in):
    ot = deepcopy(ot_in)  # Do not modify input data
    # Clean raw optitrack measurements
    # Assume faulty/missing if position stays *exactly* the same
    time = []
    e = []
    n = []
    u = []
    phi = []
    theta = []
    psi = []
    for i in range(1, len(ot.time)):
        if ot.pos_e[i] == ot.pos_e[i - 1] and ot.pos_n[i] == ot.pos_n[i - 1]:
            continue
        time.append(ot.time[i])
        e.append(ot.pos_e[i])
        n.append(ot.pos_n[i])
        u.append(ot.pos_u[i])
        phi.append(ot.rot_phi[i])
        theta.append(ot.rot_theta[i])
        psi.append(ot.rot_psi[i])
    ot.time = time
    ot.pos_e = e
    ot.pos_n = n
    ot.pos_u = u
    ot.rot_phi = phi
    ot.rot_theta = theta
    ot.rot_psi = psi
    return ot


try:
    import matplotlib.pyplot as plt

    def plot_optitrack_time(ot):
        plt.subplot(211)
        plt.plot(ot.time, ot.pos_x, label='x')
        plt.plot(ot.time, ot.pos_y, label='y')
        plt.plot(ot.time, ot.pos_z, label='z')
        plt.legend()
        plt.xlabel('Time [s]')
        plt.ylabel('[m]')
        plt.subplot(212)
        plt.plot(ot.time, np.rad2deg(ot.rot_phi), label='phi')
        plt.plot(ot.time, np.rad2deg(ot.rot_theta), label='theta')
        plt.plot(ot.time, np.rad2deg(ot.rot_psi), label='psi')
        plt.legend()
        plt.xlabel('Time [s]')
        plt.ylabel('deg')

    def plot_optitrack(ot):
        plt.plot(ot.pos_e, ot.pos_n)
        plt.plot(ot.pos_e[0], ot.pos_n[0], 'o')
        plt.xlabel('East (Optitrack) [m]')
        plt.ylabel('North (Optitrack) [m]')
        plt.axis('equal')
except:
    pass


if __name__ == '__main__':
    import argparse
    import matplotlib.pyplot as plt
    parser = argparse.ArgumentParser(description='Read optitrack csv')
    parser.add_argument('csv', type=str)
    args = parser.parse_args()

    with open(args.csv, 'rt') as f:
        ot = parse_optitrack_csv(f)

    plt.figure()
    plot_optitrack_time(ot)

    plt.figure()
    plot_optitrack(ot)

    plt.show()
