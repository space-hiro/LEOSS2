from .main import *

# import PIL

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.transforms import offset_copy
from matplotlib import gridspec
from matplotlib.widgets import Cursor
from matplotlib.widgets import Button
from matplotlib.widgets import Slider

import matplotlib.ticker as mticker
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import pandas as pd
import numpy as np

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature.nightshade import Nightshade
from shapely.geometry import Polygon
from cartopy.geodesic import Geodesic

from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def visual_check():
    s = LEOSS()
    return s

def animatedAttitudeTrack(recorder: Recorder, sample: int = 0, saveas: str = "mp4", dpi: int = 300, frameRef: str = 'Inertial'):

    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system = spacecraft.system

    xs =spacecraft.size.x/min(spacecraft.size)
    ys =spacecraft.size.y/min(spacecraft.size)
    zs =spacecraft.size.z/min(spacecraft.size)

    ratio = max(spacecraft.size)/min(spacecraft.size)

    if sample > 0:
        df1 = df.iloc[::sample,:]   
        df2 = df.iloc[df.index[-1]:,:]
        df1 = pd.concat([df1, df2], ignore_index=True, axis=0)
    
    elif sample == 0:
        df1 = df

    States      = [ item for item in df1['State'].values.tolist()[:] ]
    Positions   = [ item.position for item in df1['State'].values.tolist()[:] ]
    Velocities  = [ item.velocity for item in df1['State'].values.tolist()[:] ]
    Quaternions = [ item.quaternion for item in df1['State'].values.tolist()[:] ]
    Bodyrates   = [ item.bodyrate*R2D for item in df1['State'].values.tolist()[:] ]
    Datetimes   = [ item for item in df1['Datetime'] ][:]
    Times       = [ (item - system.datetime0).total_seconds() for item in df1['Datetime'][:] ]

    fig = plt.figure(figsize=(18,9))
    fig.tight_layout()
    ax1 = fig.add_subplot(3,2,2)
    ax2 = fig.add_subplot(3,2,4)
    ax3 = fig.add_subplot(3,2,6)
    ax4 = fig.add_subplot(2,4,1, projection='3d')
    ax5 = fig.add_subplot(2,4,2, projection='3d')
    ax6 = fig.add_subplot(2,4,5, projection='3d')
    ax7 = fig.add_subplot(2,4,6, projection='3d')

    QuatW = [ q.w for q in Quaternions ]
    QuatX = [ q.x for q in Quaternions ]
    QuatY = [ q.y for q in Quaternions ]
    QuatZ = [ q.z for q in Quaternions ]
    RateX = [ r.x for r in Bodyrates ]
    RateY = [ r.y for r in Bodyrates ]
    RateZ = [ r.z for r in Bodyrates ]

    Eulers = [ q.YPR_toRPY_vector() for q in Quaternions ]
    Roll  = [ item.x*R2D for item in Eulers ]
    Pitch = [ item.y*R2D for item in Eulers ]
    Yaw   = [ item.z*R2D for item in Eulers ]

    Matrices = [ q.toMatrix().transpose() for q in Quaternions ]

    ln1, = ax1.plot([],[], label='q0')
    ln2, = ax1.plot([],[], label='q1')
    ln3, = ax1.plot([],[], label='q2')
    ln4, = ax1.plot([],[], label='q3')

    ln5, = ax2.plot([],[], label='X')
    ln6, = ax2.plot([],[], label='Y')
    ln7, = ax2.plot([],[], label='Z')

    ln8, = ax3.plot([],[], label='roll')
    ln9, = ax3.plot([],[], label='pitch')
    ln10, = ax3.plot([],[], label='yaw')

    ln11, = ax4.plot([],[],[])
    ln12, = ax4.plot([],[],[])
    ln13, = ax4.plot([],[],[])
    ln14, = ax4.plot([],[],[])

    ln15, = ax5.plot([],[],[])
    ln16, = ax5.plot([],[],[])
    ln17, = ax5.plot([],[],[])

    ln18, = ax6.plot([],[],[])
    ln19, = ax6.plot([],[],[])
    ln20, = ax6.plot([],[],[])

    ln21, = ax7.plot([],[],[])
    ln22, = ax7.plot([],[],[])
    ln23, = ax7.plot([],[],[])
    
    ax1.grid(visible=True)
    ax2.grid(visible=True)
    ax3.grid(visible=True)

    ax4.view_init(30,20)
    ax5.view_init(0,0)
    ax6.view_init(0,90)
    ax7.view_init(90,0)

    ax1.set_title(f'Quaternion', fontsize=10)
    ax2.set_title(f'Body Rates (deg/s)', fontsize=10)
    ax3.set_title(f'Euler Angles (deg)', fontsize=10)

    def init():
        ax1.set_ylim(-1.1,1.1)
        ax3.set_ylim(-190,190)

        for axis in ax5.xaxis, ax6.yaxis, ax7.zaxis:
            axis.set_label_position('none')
            axis.set_ticks_position('none')

        ax6.zaxis.set_label_position('upper')
        ax6.zaxis.set_ticks_position('upper')    

        plt.subplots_adjust(wspace=0.1, hspace=0.3, left=None, right=None)   

        return ln1, ln2, ln3, ln4, ln5, ln6, ln7, ln8, ln9, ln10, ln11, ln12, ln13, ln14, \
                ln15, ln16, ln17, ln18, ln19, ln20, ln21, ln22, ln23,

    def update(frame):
        datetimeText = Datetimes[frame].strftime("%Y-%m-%d %H:%M:%S.%f")
        plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

        ln1.set_data(Times[0: frame], QuatW[0: frame])
        ln2.set_data(Times[0: frame], QuatX[0: frame])
        ln3.set_data(Times[0: frame], QuatY[0: frame])
        ln4.set_data(Times[0: frame], QuatZ[0: frame])
        ln5.set_data(Times[0: frame], RateX[0: frame])
        ln6.set_data(Times[0: frame], RateY[0: frame])
        ln7.set_data(Times[0: frame], RateZ[0: frame])
        ln8.set_data(Times[0: frame], Roll[0: frame])
        ln9.set_data(Times[0: frame], Pitch[0: frame])
        ln10.set_data(Times[0: frame], Yaw[0: frame])    

        ln1.set_label("q0 = "+str('%+.4F' % QuatW[frame]))
        ln2.set_label("q1 = "+str('%+.4F' % QuatX[frame]))
        ln3.set_label('q2 = '+str('%+.4F' % QuatY[frame]))
        ln4.set_label('q3 = '+str('%+.4F' % QuatZ[frame]))
        ax1.legend(loc='lower left', prop={'family':'monospace'}, ncol=4)    

        ln5.set_label("X = "+str('%+.4F' % RateX[frame]))
        ln6.set_label("Y = "+str('%+.4F' % RateY[frame]))
        ln7.set_label('Z = '+str('%+.4F' % RateZ[frame]))
        ax2.legend(loc='lower left', prop={'family':'monospace'}, ncol=3)   

        ln8.set_label("Roll = "+str('%+.4F' % Roll[frame]))
        ln9.set_label("Pitch = "+str('%+.4F' % Pitch[frame]))
        ln10.set_label('Yaw = '+str('%+.4F' % Yaw[frame]))
        ax3.legend(loc='lower left', prop={'family':'monospace'}, ncol=3)  

        xaxis = Vector(1,0,0)
        yaxis = Vector(0,1,0)
        zaxis = Vector(0,0,1)
        maxis = Matrices[frame] * spacecraft.inertia*Bodyrates[frame]

        Rotation = Matrices[frame]
        maxisLine = maxis.normalize() * ratio * 2

        if frameRef == 'Momentum':
            maxisZ = maxis.normalize()
            if maxisZ.cross(zaxis).magnitude() == 0:
                maxisX = maxisZ.cross(xaxis).normalize()
            else:
                maxisX = maxisZ.cross(zaxis).normalize()
            maxisY = maxisZ.cross(maxisX).normalize()
            MomentumRotation = Matrix(maxisX, maxisY,maxisZ)

            Rotation = MomentumRotation.transpose() * Matrices[frame]
            maxisLine = MomentumRotation.transpose() * maxis.normalize() * ratio * 2

        if frameRef == 'Orbit':
            Raxis = Positions[frame].normalize()
            Vaxis = Velocities[frame].normalize()
            Haxis = Raxis.cross(Vaxis)
            Taxis = Haxis.cross(Raxis)
            OrbitRotation = Matrix(Taxis, -1*Haxis, -1*Raxis)

            Rotation = OrbitRotation.transpose() * Matrices[frame]
            maxisLine = OrbitRotation.transpose() * maxis.normalize() * ratio * 2

        xaxis = Rotation * xaxis * xs * 2
        yaxis = Rotation * yaxis * ys * 2
        zaxis = Rotation * zaxis * zs * 2

        xFaceP1 = Rotation * Vector( xs,-ys, zs)
        xFaceP2 = Rotation * Vector( xs, ys, zs)
        xFaceP3 = Rotation * Vector( xs, ys,-zs)
        xFaceP4 = Rotation * Vector( xs,-ys,-zs)

        nxFaceP1 = Rotation * Vector(-xs, ys, zs)
        nxFaceP2 = Rotation * Vector(-xs,-ys, zs)
        nxFaceP3 = Rotation * Vector(-xs,-ys,-zs)
        nxFaceP4 = Rotation * Vector(-xs, ys,-zs)

        yFaceP1 = Rotation * Vector( xs, ys, zs)
        yFaceP2 = Rotation * Vector(-xs, ys, zs)
        yFaceP3 = Rotation * Vector(-xs, ys,-zs)
        yFaceP4 = Rotation * Vector( xs, ys,-zs)

        nyFaceP1 = Rotation * Vector(-xs,-ys, zs)
        nyFaceP2 = Rotation * Vector( xs,-ys, zs)
        nyFaceP3 = Rotation * Vector( xs,-ys,-zs)
        nyFaceP4 = Rotation * Vector(-xs,-ys,-zs)

        zFaceP1 = Rotation * Vector(-xs,-ys, zs)
        zFaceP2 = Rotation * Vector(-xs, ys, zs)
        zFaceP3 = Rotation * Vector( xs, ys, zs)
        zFaceP4 = Rotation * Vector( xs,-ys, zs)

        nzFaceP1 = Rotation * Vector(-xs,-ys,-zs)
        nzFaceP2 = Rotation * Vector(-xs, ys,-zs)
        nzFaceP3 = Rotation * Vector( xs, ys,-zs)
        nzFaceP4 = Rotation * Vector( xs,-ys,-zs)

        xFaceX = np.array([xFaceP1.x, xFaceP2.x, xFaceP3.x, xFaceP4.x])
        xFaceY = np.array([xFaceP1.y, xFaceP2.y, xFaceP3.y, xFaceP4.y])
        xFaceZ = np.array([xFaceP1.z, xFaceP2.z, xFaceP3.z, xFaceP4.z])

        nxFaceX = np.array([nxFaceP1.x, nxFaceP2.x, nxFaceP3.x, nxFaceP4.x])
        nxFaceY = np.array([nxFaceP1.y, nxFaceP2.y, nxFaceP3.y, nxFaceP4.y])
        nxFaceZ = np.array([nxFaceP1.z, nxFaceP2.z, nxFaceP3.z, nxFaceP4.z])

        yFaceX = np.array([yFaceP1.x, yFaceP2.x, yFaceP3.x, yFaceP4.x])
        yFaceY = np.array([yFaceP1.y, yFaceP2.y, yFaceP3.y, yFaceP4.y])
        yFaceZ = np.array([yFaceP1.z, yFaceP2.z, yFaceP3.z, yFaceP4.z])

        nyFaceX = np.array([nyFaceP1.x, nyFaceP2.x, nyFaceP3.x, nyFaceP4.x])
        nyFaceY = np.array([nyFaceP1.y, nyFaceP2.y, nyFaceP3.y, nyFaceP4.y])
        nyFaceZ = np.array([nyFaceP1.z, nyFaceP2.z, nyFaceP3.z, nyFaceP4.z])

        zFaceX = np.array([zFaceP1.x, zFaceP2.x, zFaceP3.x, zFaceP4.x])
        zFaceY = np.array([zFaceP1.y, zFaceP2.y, zFaceP3.y, zFaceP4.y])
        zFaceZ = np.array([zFaceP1.z, zFaceP2.z, zFaceP3.z, zFaceP4.z])

        nzFaceX = np.array([nzFaceP1.x, nzFaceP2.x, nzFaceP3.x, nzFaceP4.x])
        nzFaceY = np.array([nzFaceP1.y, nzFaceP2.y, nzFaceP3.y, nzFaceP4.y])
        nzFaceZ = np.array([nzFaceP1.z, nzFaceP2.z, nzFaceP3.z, nzFaceP4.z])

        xFace = np.zeros([4,3])
        xFace[:,0] = xFaceX
        xFace[:,1] = xFaceY
        xFace[:,2] = xFaceZ

        nxFace = np.zeros([4,3])
        nxFace[:,0] = nxFaceX
        nxFace[:,1] = nxFaceY
        nxFace[:,2] = nxFaceZ

        yFace = np.zeros([4,3])
        yFace[:,0] = yFaceX
        yFace[:,1] = yFaceY
        yFace[:,2] = yFaceZ

        nyFace = np.zeros([4,3])
        nyFace[:,0] = nyFaceX
        nyFace[:,1] = nyFaceY
        nyFace[:,2] = nyFaceZ

        zFace = np.zeros([4,3])
        zFace[:,0] = zFaceX
        zFace[:,1] = zFaceY
        zFace[:,2] = zFaceZ

        nzFace = np.zeros([4,3])
        nzFace[:,0] = nzFaceX
        nzFace[:,1] = nzFaceY
        nzFace[:,2] = nzFaceZ

        ax4.clear()
        ax4.set_xlim(-ratio,ratio)
        ax4.set_ylim(-ratio,ratio)
        ax4.set_zlim(-ratio,ratio)
        ax4.grid(False)
        ln11,  = ax4.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ln12,  = ax4.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ln13, = ax4.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ln14, = ax4.plot([0,maxisLine.x],[0,maxisLine.y],[0,maxisLine.z],c='orange',linewidth=1.0, zorder=5, linestyle='-')
        ax4.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax4.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        scale = 2.0
        ax5.clear()
        ax5.set_xlim(-ratio*scale,ratio*scale)
        ax5.set_ylim(-ratio*scale,ratio*scale)
        ax5.set_zlim(-ratio*scale,ratio*scale)
        ax5.grid(False)
        ln15,  = ax5.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ln16,  = ax5.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ln17, = ax5.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax5.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax5.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        ax6.clear()
        ax6.set_xlim(-ratio*scale,ratio*scale)
        ax6.set_ylim(-ratio*scale,ratio*scale)
        ax6.set_zlim(-ratio*scale,ratio*scale)
        ax6.grid(False)
        ln18,  = ax6.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ln19,  = ax6.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ln20, = ax6.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax6.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax6.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        ax7.clear()
        ax7.set_xlim(-ratio*scale,ratio*scale)
        ax7.set_ylim(-ratio*scale,ratio*scale)
        ax7.set_zlim(-ratio*scale,ratio*scale)
        ax7.grid(False)
        ln21,  = ax7.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ln22,  = ax7.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ln23, = ax7.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax7.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax7.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        frameText = ''
        if frameRef == 'Inertial':
            frameText = 'ECIF'
        if frameRef == 'Momentum':
            frameText = 'Angular Momentum Vector'
        if frameRef == 'Orbit':
            frameText = 'LVLH Earth Pointing'

        ax4.set_title(f'3D View\nFrame = {frameText}', fontsize=10, fontname='monospace')
        ax5.set_title(f'Perspective Along +X', fontsize=10, fontname='monospace', y=-0.01)
        ax6.set_title(f'Perspective Along +Y', fontsize=10, fontname='monospace', y=-0.01)
        ax7.set_title(f'Perspective Along +Z', fontsize=10, fontname='monospace', y=-0.01)

        if frame > 0:
            ax1.set_xlim(Times[0]-1, Times[frame]+10)
            ax2.set_xlim(Times[0]-1, Times[frame]+10)
            ax3.set_xlim(Times[0]-1, Times[frame]+10)
            maxV = 0
            for rate in Bodyrates[0: frame]:
                lis = abs(np.array([rate.x, rate.y, rate.z]))
                if max(lis) > maxV:
                    maxV = max(lis)

            ax2.set_ylim(-1.5*maxV,1.5*maxV)

        return ln1, ln2, ln3, ln4, ln5, ln6, ln7, ln8, ln9, ln10, ln11, ln12, ln13, ln14, \
                ln15, ln16, ln17, ln18, ln19, ln20, ln21, ln22, ln23,

    print("\nRun Animation (from "+str(Times[0])+" to "+str(Times[-1])+", step="+str(Times[1]-Times[0])+")")
    anim = FuncAnimation(
        fig,
        update,
        frames = tqdm(np.arange(0, len(Times), 1), total=len(Times)-1, position=0, desc='Animating Attitude Track', bar_format='{l_bar}{bar:25}{r_bar}{bar:-25b}'),
        interval = 30,
        init_func = init,
        blit = True
    )

    if saveas == "mp4":
        anim.save("Attitudetrack.mp4", writer='ffmpeg', fps=30, dpi=dpi)
    if saveas == "gif":
        anim.save("Attitudetrack.gif", writer='pillow', fps=30)

    plt.close()

def sliderAttitudeTrack(recorder: Recorder, frameRef: str = 'Inertial'):
    global frame
    frame = 0

    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system = spacecraft.system

    xs =spacecraft.size.x/min(spacecraft.size)
    ys =spacecraft.size.y/min(spacecraft.size)
    zs =spacecraft.size.z/min(spacecraft.size)

    ratio = max(spacecraft.size)/min(spacecraft.size)

    States      = [ item for item in df['State'].values.tolist()[:] ]
    Positions   = [ item.position for item in df['State'].values.tolist()[:] ]
    Velocities  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    Quaternions = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    Bodyrates   = [ item.bodyrate*R2D for item in df['State'].values.tolist()[:] ]
    Datetimes   = [ item for item in df['Datetime'] ][:]
    Times       = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    fig = plt.figure(figsize=(18,9))
    fig.tight_layout()
    ax1 = fig.add_subplot(3,2,2)
    ax2 = fig.add_subplot(3,2,4)
    ax3 = fig.add_subplot(3,2,6)
    ax4 = fig.add_subplot(2,4,1, projection='3d')
    ax5 = fig.add_subplot(2,4,2, projection='3d')
    ax6 = fig.add_subplot(2,4,5, projection='3d')
    ax7 = fig.add_subplot(2,4,6, projection='3d')

    QuatW = [ q.w for q in Quaternions ]
    QuatX = [ q.x for q in Quaternions ]
    QuatY = [ q.y for q in Quaternions ]
    QuatZ = [ q.z for q in Quaternions ]
    RateX = [ r.x for r in Bodyrates ]
    RateY = [ r.y for r in Bodyrates ]
    RateZ = [ r.z for r in Bodyrates ]

    Eulers = [ q.YPR_toRPY_vector() for q in Quaternions ]
    Roll  = [ item.x*R2D for item in Eulers ]
    Pitch = [ item.y*R2D for item in Eulers ]
    Yaw   = [ item.z*R2D for item in Eulers ]

    Matrices = [ q.toMatrix().transpose() for q in Quaternions ]

    ln1, = ax1.plot([],[], label='q0')
    ln2, = ax1.plot([],[], label='q1')
    ln3, = ax1.plot([],[], label='q2')
    ln4, = ax1.plot([],[], label='q3')

    ln5, = ax2.plot([],[], label='X')
    ln6, = ax2.plot([],[], label='Y')
    ln7, = ax2.plot([],[], label='Z')

    ln8, = ax3.plot([],[], label='roll')
    ln9, = ax3.plot([],[], label='pitch')
    ln10, = ax3.plot([],[], label='yaw')

    ln11, = ax4.plot([],[],[])
    ln12, = ax4.plot([],[],[])
    ln13, = ax4.plot([],[],[])
    ln14, = ax4.plot([],[],[])

    ln15, = ax5.plot([],[],[])
    ln16, = ax5.plot([],[],[])
    ln17, = ax5.plot([],[],[])

    ln18, = ax6.plot([],[],[])
    ln19, = ax6.plot([],[],[])
    ln20, = ax6.plot([],[],[])

    ln21, = ax7.plot([],[],[])
    ln22, = ax7.plot([],[],[])
    ln23, = ax7.plot([],[],[])
    
    ax1.grid(visible=True)
    ax2.grid(visible=True)
    ax3.grid(visible=True)

    ax4.view_init(30,20)
    ax5.view_init(0,0)
    ax6.view_init(0,90)
    ax7.view_init(90,0)

    ax1.set_title(f'Quaternion', fontsize=10)
    ax2.set_title(f'Body Rates (deg/s)', fontsize=10)
    ax3.set_title(f'Euler Angles (deg)', fontsize=10)

    def init():
        ax1.set_ylim(-1.1,1.1)
        ax3.set_ylim(-190,190)

        for axis in ax5.xaxis, ax6.yaxis, ax7.zaxis:
            axis.set_label_position('none')
            axis.set_ticks_position('none')

        ax6.zaxis.set_label_position('upper')
        ax6.zaxis.set_ticks_position('upper')    

        plt.subplots_adjust(wspace=0.1, hspace=0.3, left=None, right=None, bottom=0.2)   

    def update(input):
        global frame 
        frame = int(input)
        frame = int(frame)
        datetimeText = Datetimes[frame].strftime("%Y-%m-%d %H:%M:%S.%f")
        plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

        ln1.set_data(Times[0: frame], QuatW[0: frame])
        ln2.set_data(Times[0: frame], QuatX[0: frame])
        ln3.set_data(Times[0: frame], QuatY[0: frame])
        ln4.set_data(Times[0: frame], QuatZ[0: frame])
        ln5.set_data(Times[0: frame], RateX[0: frame])
        ln6.set_data(Times[0: frame], RateY[0: frame])
        ln7.set_data(Times[0: frame], RateZ[0: frame])
        ln8.set_data(Times[0: frame], Roll[0: frame])
        ln9.set_data(Times[0: frame], Pitch[0: frame])
        ln10.set_data(Times[0: frame], Yaw[0: frame])    

        ln1.set_label("q0 = "+str('%+.4F' % QuatW[frame]))
        ln2.set_label("q1 = "+str('%+.4F' % QuatX[frame]))
        ln3.set_label('q2 = '+str('%+.4F' % QuatY[frame]))
        ln4.set_label('q3 = '+str('%+.4F' % QuatZ[frame]))
        ax1.legend(loc='lower left', prop={'family':'monospace'}, ncol=4)    

        ln5.set_label("X = "+str('%+.4F' % RateX[frame]))
        ln6.set_label("Y = "+str('%+.4F' % RateY[frame]))
        ln7.set_label('Z = '+str('%+.4F' % RateZ[frame]))
        ax2.legend(loc='lower left', prop={'family':'monospace'}, ncol=3)   

        ln8.set_label("Roll = "+str('%+.4F' % Roll[frame]))
        ln9.set_label("Pitch = "+str('%+.4F' % Pitch[frame]))
        ln10.set_label('Yaw = '+str('%+.4F' % Yaw[frame]))
        ax3.legend(loc='lower left', prop={'family':'monospace'}, ncol=3)  

        xaxis = Vector(1,0,0)
        yaxis = Vector(0,1,0)
        zaxis = Vector(0,0,1)
        maxis = Matrices[frame] * spacecraft.inertia*Bodyrates[frame]
        

        Rotation = Matrices[frame]

        if maxis.magnitude() == 0:
            maxis = Vector(1,0,0)

        maxisLine = maxis.normalize() * ratio * 2

        if frameRef == 'Momentum':
            maxisZ = maxis.normalize()
            if maxisZ.cross(zaxis).magnitude() == 0:
                maxisX = maxisZ.cross(xaxis).normalize()
            else:
                maxisX = maxisZ.cross(zaxis).normalize()
            maxisY = maxisZ.cross(maxisX).normalize()
            MomentumRotation = Matrix(maxisX, maxisY,maxisZ)

            Rotation = MomentumRotation.transpose() * Matrices[frame]
            maxisLine = MomentumRotation.transpose() * maxis.normalize() * ratio * 2

        if frameRef == 'Orbit':
            Raxis = Positions[frame].normalize()
            Vaxis = Velocities[frame].normalize()
            Haxis = Raxis.cross(Vaxis)
            Taxis = Haxis.cross(Raxis)
            OrbitRotation = Matrix(Taxis, -1*Haxis, -1*Raxis)

            Rotation = OrbitRotation.transpose() * Matrices[frame]
            maxisLine = OrbitRotation.transpose() * maxis.normalize() * ratio * 2

        xaxis = Rotation * xaxis * xs * 2
        yaxis = Rotation * yaxis * ys * 2
        zaxis = Rotation * zaxis * zs * 2

        xFaceP1 = Rotation * Vector( xs,-ys, zs)
        xFaceP2 = Rotation * Vector( xs, ys, zs)
        xFaceP3 = Rotation * Vector( xs, ys,-zs)
        xFaceP4 = Rotation * Vector( xs,-ys,-zs)

        nxFaceP1 = Rotation * Vector(-xs, ys, zs)
        nxFaceP2 = Rotation * Vector(-xs,-ys, zs)
        nxFaceP3 = Rotation * Vector(-xs,-ys,-zs)
        nxFaceP4 = Rotation * Vector(-xs, ys,-zs)

        yFaceP1 = Rotation * Vector( xs, ys, zs)
        yFaceP2 = Rotation * Vector(-xs, ys, zs)
        yFaceP3 = Rotation * Vector(-xs, ys,-zs)
        yFaceP4 = Rotation * Vector( xs, ys,-zs)

        nyFaceP1 = Rotation * Vector(-xs,-ys, zs)
        nyFaceP2 = Rotation * Vector( xs,-ys, zs)
        nyFaceP3 = Rotation * Vector( xs,-ys,-zs)
        nyFaceP4 = Rotation * Vector(-xs,-ys,-zs)

        zFaceP1 = Rotation * Vector(-xs,-ys, zs)
        zFaceP2 = Rotation * Vector(-xs, ys, zs)
        zFaceP3 = Rotation * Vector( xs, ys, zs)
        zFaceP4 = Rotation * Vector( xs,-ys, zs)

        nzFaceP1 = Rotation * Vector(-xs,-ys,-zs)
        nzFaceP2 = Rotation * Vector(-xs, ys,-zs)
        nzFaceP3 = Rotation * Vector( xs, ys,-zs)
        nzFaceP4 = Rotation * Vector( xs,-ys,-zs)

        xFaceX = np.array([xFaceP1.x, xFaceP2.x, xFaceP3.x, xFaceP4.x])
        xFaceY = np.array([xFaceP1.y, xFaceP2.y, xFaceP3.y, xFaceP4.y])
        xFaceZ = np.array([xFaceP1.z, xFaceP2.z, xFaceP3.z, xFaceP4.z])

        nxFaceX = np.array([nxFaceP1.x, nxFaceP2.x, nxFaceP3.x, nxFaceP4.x])
        nxFaceY = np.array([nxFaceP1.y, nxFaceP2.y, nxFaceP3.y, nxFaceP4.y])
        nxFaceZ = np.array([nxFaceP1.z, nxFaceP2.z, nxFaceP3.z, nxFaceP4.z])

        yFaceX = np.array([yFaceP1.x, yFaceP2.x, yFaceP3.x, yFaceP4.x])
        yFaceY = np.array([yFaceP1.y, yFaceP2.y, yFaceP3.y, yFaceP4.y])
        yFaceZ = np.array([yFaceP1.z, yFaceP2.z, yFaceP3.z, yFaceP4.z])

        nyFaceX = np.array([nyFaceP1.x, nyFaceP2.x, nyFaceP3.x, nyFaceP4.x])
        nyFaceY = np.array([nyFaceP1.y, nyFaceP2.y, nyFaceP3.y, nyFaceP4.y])
        nyFaceZ = np.array([nyFaceP1.z, nyFaceP2.z, nyFaceP3.z, nyFaceP4.z])

        zFaceX = np.array([zFaceP1.x, zFaceP2.x, zFaceP3.x, zFaceP4.x])
        zFaceY = np.array([zFaceP1.y, zFaceP2.y, zFaceP3.y, zFaceP4.y])
        zFaceZ = np.array([zFaceP1.z, zFaceP2.z, zFaceP3.z, zFaceP4.z])

        nzFaceX = np.array([nzFaceP1.x, nzFaceP2.x, nzFaceP3.x, nzFaceP4.x])
        nzFaceY = np.array([nzFaceP1.y, nzFaceP2.y, nzFaceP3.y, nzFaceP4.y])
        nzFaceZ = np.array([nzFaceP1.z, nzFaceP2.z, nzFaceP3.z, nzFaceP4.z])

        xFace = np.zeros([4,3])
        xFace[:,0] = xFaceX
        xFace[:,1] = xFaceY
        xFace[:,2] = xFaceZ

        nxFace = np.zeros([4,3])
        nxFace[:,0] = nxFaceX
        nxFace[:,1] = nxFaceY
        nxFace[:,2] = nxFaceZ

        yFace = np.zeros([4,3])
        yFace[:,0] = yFaceX
        yFace[:,1] = yFaceY
        yFace[:,2] = yFaceZ

        nyFace = np.zeros([4,3])
        nyFace[:,0] = nyFaceX
        nyFace[:,1] = nyFaceY
        nyFace[:,2] = nyFaceZ

        zFace = np.zeros([4,3])
        zFace[:,0] = zFaceX
        zFace[:,1] = zFaceY
        zFace[:,2] = zFaceZ

        nzFace = np.zeros([4,3])
        nzFace[:,0] = nzFaceX
        nzFace[:,1] = nzFaceY
        nzFace[:,2] = nzFaceZ

        ax4.clear()
        ax4.set_xlim(-ratio,ratio)
        ax4.set_ylim(-ratio,ratio)
        ax4.set_zlim(-ratio,ratio)
        ax4.grid(False)
        ax4.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ax4.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ax4.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax4.plot([0,maxisLine.x],[0,maxisLine.y],[0,maxisLine.z],c='orange',linewidth=1.0, zorder=5, linestyle='-')
        ax4.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax4.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        scale = 2.0
        ax5.clear()
        ax5.set_xlim(-ratio*scale,ratio*scale)
        ax5.set_ylim(-ratio*scale,ratio*scale)
        ax5.set_zlim(-ratio*scale,ratio*scale)
        ax5.grid(False)
        ax5.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ax5.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ax5.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax5.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax5.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        ax6.clear()
        ax6.set_xlim(-ratio*scale,ratio*scale)
        ax6.set_ylim(-ratio*scale,ratio*scale)
        ax6.set_zlim(-ratio*scale,ratio*scale)
        ax6.grid(False)
        ax6.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ax6.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ax6.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax6.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax6.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        ax7.clear()
        ax7.set_xlim(-ratio*scale,ratio*scale)
        ax7.set_ylim(-ratio*scale,ratio*scale)
        ax7.set_zlim(-ratio*scale,ratio*scale)
        ax7.grid(False)
        ax7.plot([0,xaxis.x],[0,xaxis.y],[0,xaxis.z],c='red',   linewidth=1.0, zorder=5, linestyle='--')
        ax7.plot([0,yaxis.x],[0,yaxis.y],[0,yaxis.z],c='green', linewidth=1.0, zorder=5, linestyle='--')
        ax7.plot([0,zaxis.x],[0,zaxis.y],[0,zaxis.z],c='blue',  linewidth=1.0, zorder=5, linestyle='--')
        ax7.add_collection(Poly3DCollection([xFace, yFace, zFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))
        ax7.add_collection(Poly3DCollection([nxFace, nyFace, nzFace], facecolors='cyan', linewidths=1, edgecolors='k', alpha=.50))

        frameText = ''
        if frameRef == 'Inertial':
            frameText = 'ECIF'
        if frameRef == 'Momentum':
            frameText = 'Angular Momentum Vector'
        if frameRef == 'Orbit':
            frameText = 'LVLH Earth Pointing'

        ax4.set_title(f'3D View\nFrame = {frameText}', fontsize=10, fontname='monospace')
        ax5.set_title(f'Perspective Along +X', fontsize=10, fontname='monospace', y=-0.01)
        ax6.set_title(f'Perspective Along +Y', fontsize=10, fontname='monospace', y=-0.01)
        ax7.set_title(f'Perspective Along +Z', fontsize=10, fontname='monospace', y=-0.01)

        if frame > 0:
            ax1.set_xlim(Times[0]-1, Times[frame]+10)
            ax2.set_xlim(Times[0]-1, Times[frame]+10)
            ax3.set_xlim(Times[0]-1, Times[frame]+10)
            maxV = 0
            for rate in Bodyrates[0: frame]:
                lis = abs(np.array([rate.x, rate.y, rate.z]))
                if max(lis) > maxV:
                    maxV = max(lis)

            ax2.set_ylim(-1.5*maxV,1.5*maxV)

    init()
    update(0)

    axtime = fig.add_axes([0.2, 0.1, 0.65, 0.03])
    time_slider = Slider(
        ax      = axtime,
        label   = "TimeStep",
        valmin  = 0,
        valmax  = len(Times)-1,
        valinit = 0,
        valstep = 1,
        color   = 'green'
    )
    forwardax = fig.add_axes([0.55, 0.025, 0.1, 0.04])
    backwardax = fig.add_axes([0.45, 0.025, 0.1, 0.04])
    buttonF = Button(forwardax, '>', hovercolor='0.975')
    buttonB = Button(backwardax, '<', hovercolor='0.975')

    def forward(event):
        global frame
        frame = frame + 1
        update(frame)
        time_slider.set_val(frame)

    def backward(event):
        global frame
        frame = frame - 1
        update(frame)
        time_slider.set_val(frame)

    buttonF.on_clicked(forward)
    buttonB.on_clicked(backward)


    time_slider.on_changed(update)

    plt.show()

def attitudeTrack(recorder: Recorder):

    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    Quaternions = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    Bodyrates   = [ item.bodyrate*R2D for item in df['State'].values.tolist()[:] ]
    Datetimes   = [ item for item in df['Datetime'] ][:]
    Times       = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    fig = plt.figure(figsize=(12,6))
    ax1 = fig.add_subplot(3,1,1)
    ax2 = fig.add_subplot(3,1,2)
    ax3 = fig.add_subplot(3,1,3)

    QuatW = [ q.w for q in Quaternions ]
    QuatX = [ q.x for q in Quaternions ]
    QuatY = [ q.y for q in Quaternions ]
    QuatZ = [ q.z for q in Quaternions ]
    RateX = [ r.x for r in Bodyrates ]
    RateY = [ r.y for r in Bodyrates ]
    RateZ = [ r.z for r in Bodyrates ]

    Eulers = [ q.YPR_toRPY_vector() for q in Quaternions ]
    Roll  = [ item.x*R2D for item in Eulers ]
    Pitch = [ item.y*R2D for item in Eulers ]
    Yaw   = [ item.z*R2D for item in Eulers ]

    ax1.plot(Times, QuatW, label='q0')
    ax1.plot(Times, QuatX, label='q1')
    ax1.plot(Times, QuatY, label='q2')
    ax1.plot(Times, QuatZ, label='q3')
    ax1.grid()
    ax1.legend(bbox_to_anchor=(1, 0.5), loc="center left", prop={'family':'monospace'})

    ax2.plot(Times, RateX, label='X')
    ax2.plot(Times, RateY, label='Y')
    ax2.plot(Times, RateZ, label='Z')
    ax2.grid()
    ax2.legend(bbox_to_anchor=(1, 0.5), loc="center left", prop={'family':'monospace'})   

    ax3.plot(Times, Roll, label='roll')
    ax3.plot(Times, Pitch, label='pitch')
    ax3.plot(Times, Yaw, label='yaw')
    ax3.grid()
    ax3.legend(bbox_to_anchor=(1, 0.5), loc="center left", prop={'family':'monospace'})

    ax1.set_title(f'Quaternion', fontsize=10)
    ax2.set_title(f'Body Rates (deg/s)', fontsize=10)
    ax3.set_title(f'Euler Angles (deg)', fontsize=10)
    ax3.set_xlabel("Time (s)")

    plt.suptitle(f'{spacecraft.name}\n{Datetimes[-1]}', fontname='monospace')
    plt.subplots_adjust(hspace=0.4)   
    plt.show()

def groundTrack(recorder: Recorder, dateTime = -1):

    # get datadict from recorder as dataframe
    df = pd.DataFrame.from_dict(recorder.dataDict)

    # variable for spacecraft and system
    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    # split data columns from recorder into components
    SunLocation = [ item for item in df['Sunlocation'].values.tolist()[:] ]
    Latitudes  = [ item[0] for item in df['Location'].values.tolist()[:] ]
    Longitudes = [ item[1] for item in df['Location'].values.tolist()[:] ]
    Altitudes  = [ item[2] for item in df['Location'].values.tolist()[:] ]
    Datetimes  = [ item for item in df['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    # initialize figure and projection 
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # add the default global map
    ax.stock_img()

    # create gridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='white', alpha = 0.25,
                  linestyle='--')

    # labels on bottom and left axes
    gl.top_labels  = False
    gl.right_labels = False

    # define the label style
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}

    # now we define exactly which ones to label and spruce up the labels
    longitude_list = list(range(-180,180+45,45))
    latitude_list  = list(range(-90,90+20,20))
    gl.xlocator    = mticker.FixedLocator(longitude_list)
    gl.ylocator    = mticker.FixedLocator(latitude_list)
    gl.xformatter  = LONGITUDE_FORMATTER
    gl.yformatter  = LATITUDE_FORMATTER

    # plot the scatter points for longitude and latitude track
    plot = plt.scatter(Longitudes, Latitudes,
        color='red', s=0.2, zorder=2.5,
        transform=ccrs.PlateCarree(),
        )
    
    # if datetime input is -1 then set the datetime as current datetime (plot all from Start to End)
    if dateTime == -1:
        dateTime = system.datenow()

    # replace datetime input as a datetime object, from int or float
    currentTime = 0
    if isinstance(dateTime, datetime.datetime):
        delta = (Datetimes[1] - Datetimes[0]).total_seconds()
        currentTime = (dateTime - system.datetime0).total_seconds() - delta
    elif isinstance(dateTime, int) or isinstance(dateTime, float):
        if dateTime > Times[0] and dateTime <= Times[-1]:
            currentTime = dateTime
            dateTime = (system.datetime0+datetime.timedelta(seconds=currentTime))
        else:
            raise ValueError("Datetime input should be a valid time")
    else:
        raise TypeError("Datetime input should be int, float or datettime type")
    
    # create a super title with name of spacecraft and datetime
    plt.suptitle(f'{spacecraft.name}\n{dateTime}')

    # set the visibility of the track to only show the track from start time to the input time
    plot.set_alpha([ item<=currentTime for item in Times])

    # show the nightshade transition on the global map
    ax.add_feature(Nightshade(dateTime, alpha=0.3))

    # create a spot on the current location given the time
    index = Times.index(currentTime)
    spot, = ax.plot(Longitudes[index], Latitudes[index] , marker='o', color='white', markersize=12,
            alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)
    
    sun, = ax.plot(SunLocation[index].y, SunLocation[index].x , marker='o', color='yellow', markersize=12,
        alpha=1.0, transform=ccrs.PlateCarree(), zorder=3.0)

    
    # create a legend on the current location with details on lat,lon and lat
    lat = str('%.2F'% Latitudes[index]+"°")
    lon = str('%.2F'% Longitudes[index]+"°")
    alt = str('%.2F'% Altitudes[index]+"km")
    txt = "lat: "+lat+"\nlon: "+lon+"\nalt: "+alt
    geodetic_transform = ccrs.PlateCarree()._as_mpl_transform(ax)
    text_transform = offset_copy(geodetic_transform, units='dots', x=+15, y=+0)

    label = ax.text(Longitudes[index], Latitudes[index], txt,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=8,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})

    plt.show()

def passTrack(recorder: Recorder, groundstation: GroundStation, dateTime = -1):

    # get datadict from recorder as dataframe
    df = pd.DataFrame.from_dict(recorder.dataDict)

    # variable for spacecraft and system
    spacecraft = recorder.attachedTo
    system     = spacecraft.system
    station    = groundstation

    # split data columns from recorder into components
    SunLocation = [ item for item in df['Sunlocation'].values.tolist()[:] ]
    Positions   = [ item.position for item in df['State'].values.tolist()[:] ]
    Latitudes   = [ item[0] for item in df['Location'].values.tolist()[:] ]
    Longitudes  = [ item[1] for item in df['Location'].values.tolist()[:] ]
    Altitudes   = [ item[2] for item in df['Location'].values.tolist()[:] ]
    Datetimes   = [ item for item in df['Datetime'] ][:]
    Times       = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    Passes = []
    passing = False
    start = None
    end   = None
    high  = None
    radius = None
    for index in np.arange(0, len(Positions), 1):
        position = Positions[index]
        time = Times[index]
        gmst_ = system.gmst + time*(360.98564724)/(24*3600) 

        latitude  = station.latitude
        longitude = station.longitude
        altitude  = station.altitude

        longitude = longitude + gmst_

        if longitude < 0:
            longitude = (((longitude/360) - int(longitude/360)) * 360) + 360    
        if longitude > 180:
            longitude = -360 + longitude

        x = math.cos(longitude*D2R)*math.cos(latitude*D2R)
        y = math.sin(longitude*D2R)*math.cos(latitude*D2R)
        z = math.sin(latitude*D2R)

        target = Vector(x, y, z) * (system.radi + altitude)

        target2pos = position - target

        angle = math.acos( (target.normalize() * target2pos.normalize()).sum() ) * R2D
        angle = 90 - angle - station.min_elevation

        if (angle >= 0) and (passing == False):
            start = Datetimes[index]
            end = None
            passing = True
            high = [angle, start]
            # print('Entered')
        if (angle >= 0) and (passing == True):
            if angle > high[0]:
                high =  [angle, Datetimes[index]] 
        if angle < 0 and passing == True:
            end = Datetimes[index]
            passing = False
            newPass = Pass(start, high[1], high[0]+station.min_elevation, end)
            Passes.append(newPass)
            radius = (position.normalize()*system.radi - target.normalize()*system.radi).magnitude()

            start = None
            end = None
            print("#"+str(len(Passes))+":\t"+str(newPass))
            # print('Exit')

    # initialize figure and projection 
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # add the default global map
    img = plt.imread("NE1_50M_SR_W.tif")
    # img = plt.imread("blue_marble_14MB.png")
    # img = plt.imread("blue_marble_181MB.png")
    # PIL.Image.MAX_IMAGE_PIXELS = 233280000
    # img = plt.imread("blue_marble_26MB.jpg")
    ax.imshow(img, origin='upper', extent=(-180, 180, -90, 90), transform=ccrs.PlateCarree(), vmin=0, vmax=255)
    ext = 25
    ax.set_extent([ station.longitude-ext, station.longitude+ext, station.latitude-ext, station.latitude+ext ], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, edgecolor="black", ls="-", lw=0.5)

    # create gridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='white', alpha = 0.25,
                  linestyle='--')

    # labels on bottom and left axes
    gl.top_labels = False
    gl.right_labels = False

    # define the label style
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}

    # now we define exactly which ones to label and spruce up the labels
    longitude_list = list(range(-180,180+2,2))
    latitude_list = list(range(-90,90+2,2))
    gl.xlocator = mticker.FixedLocator(longitude_list)
    gl.ylocator = mticker.FixedLocator(latitude_list)
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    # plot the scatter points for longitude and latitude track
    plot = plt.scatter(Longitudes, Latitudes,
        color='red', s=0.2, zorder=2.5,
        transform=ccrs.PlateCarree(),
        )
    
    # if datetime input is -1 then set the datetime as current datetime (plot all from Start to End)
    if dateTime == -1:
        dateTime = system.datenow()

    # replace datetime input as a datetime object, from int or float
    currentTime = 0
    if isinstance(dateTime, datetime.datetime):
        delta = (Datetimes[1] - Datetimes[0]).total_seconds()
        currentTime = (dateTime - system.datetime0).total_seconds() - delta
    elif isinstance(dateTime, int) or isinstance(dateTime, float):
        if dateTime > Times[0] and dateTime <= Times[-1]:
            currentTime = dateTime
            dateTime = (system.datetime0+datetime.timedelta(seconds=currentTime))
        else:
            raise ValueError("Datetime input should valid time")
    else:
        raise TypeError("Datetime input should be int, float or datettime type")

    # set the visibility of the track to only show the track from start time to the input time
    currentpass = Passes[0]
    startpass = (currentpass.AOS - system.datetime0).total_seconds()
    tcapass = (currentpass.TCA - system.datetime0).total_seconds()
    endpass = (currentpass.LOS - system.datetime0).total_seconds()
    plot.set_alpha( [item>=startpass and item<=endpass for item in Times ])

    # create a super title with name of spacecraft and datetime
    plt.suptitle(f'{spacecraft.name}\n{currentpass.TCA}')

    # show the nightshade transition on the global map
    passTrack.ns = ax.add_feature(Nightshade(currentpass.TCA, alpha=0.3))

    # create a spot on the current location given the time
    startIndex = Times.index(startpass)
    endIndex   = Times.index(endpass)
    tcaIndex   = Times.index(tcapass)

    # A = 1 + math.tan(station.min_elevation*D2R)**2
    # B = 2 * system.radi * math.tan(station.min_elevation*D2R)
    # H = Altitudes[tcaIndex]*1000
    # C = -2 * system.radi * H - (H*H)

    # Xaos = (-B + math.sqrt(B**2 - 4*A*C)) / 2*A
    # Yaos = math.tan(station.min_elevation*D2R)*Xaos
    # M = (Yaos + system.radi) / Xaos
    # arc0 = 90 - (math.atan(M)*R2D)
    # print(arc0)

    # arc = math.acos(system.radi/(Altitudes[tcaIndex]*1000 + system.radi))
    # radius = arc0*D2R * (system.radi + Altitudes[tcaIndex]*1000)
    # ax.tissot(lons=[station.longitude], lats=[station.latitude], rad_km=500*1000, alpha=0.25, facecolor='orange', edgecolor='black')
    circle = Geodesic().circle(station.longitude, station.latitude, radius, n_samples=80)
    feature = cfeature.ShapelyFeature([Polygon(circle)], ccrs.PlateCarree(), alpha=0.2, fc='white', ec="black")
    ax.add_feature(feature)
    # print(arc*R2D)

    text_radius = str('%.2F' % (radius/1000))
    ax.set_title(f'Pass #{1}/{len(Passes)}, Ground Radius: {text_radius} km.')

    startSpot, = ax.plot(Longitudes[startIndex], Latitudes[startIndex] , marker='o', color='white', markersize=5,
            alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)
    tcaSpot, = ax.plot(Longitudes[tcaIndex], Latitudes[tcaIndex] , marker='o', color='white', markersize=5,
        alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)
    endSpot, = ax.plot(Longitudes[endIndex], Latitudes[endIndex] , marker='o', color='white', markersize=5,
        alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)
    sun, = ax.plot(SunLocation[tcaIndex].y, SunLocation[tcaIndex].x , marker='o', color='yellow', markersize=5,
        alpha=1.0, transform=ccrs.PlateCarree(), zorder=3.0)
    groundSpot, = ax.plot(station.longitude, station.latitude , marker='x', color='red', markersize=5,
        alpha=1.0, transform=ccrs.PlateCarree(), zorder=3.0)

    # create a legend on the current location with details on lat,lon and lat
    lat1 = str('%.2F'% Latitudes[startIndex]+"°")
    lon1 = str('%.2F'% Longitudes[startIndex]+"°")
    alt1 = str('%.2F'% Altitudes[startIndex]+"km")
    txt1 = "lat: "+lat1+"\nlon: "+lon1+"\nalt: "+alt1
    geodetic_transform = ccrs.PlateCarree()._as_mpl_transform(ax)
    text_transform = offset_copy(geodetic_transform, units='dots', x=+15, y=+0)

    label1 = ax.text(Longitudes[startIndex], Latitudes[startIndex], txt1,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=6,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})
    
    lat2 = str('%.2F'% Latitudes[tcaIndex]+"°")
    lon2 = str('%.2F'% Longitudes[tcaIndex]+"°")
    alt2 = str('%.2F'% Altitudes[tcaIndex]+"km")
    elev = str('%.2F'% currentpass.angleTCA+"°")
    txt2 = "lat: "+lat2+"\nlon: "+lon2+"\nalt: "+alt2+"\nelev: "+elev

    label2 = ax.text(Longitudes[tcaIndex], Latitudes[tcaIndex], txt2,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=6,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})
    
    lat3 = str('%.2F'% Latitudes[endIndex]+"°")
    lon3 = str('%.2F'% Longitudes[endIndex]+"°")
    alt3 = str('%.2F'% Altitudes[endIndex]+"km")
    txt3 = "lat: "+lat3+"\nlon: "+lon3+"\nalt: "+alt3

    label3 = ax.text(Longitudes[endIndex], Latitudes[endIndex], txt3,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=6,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})

    class Index():
        ind = 0

        def next(self, event):
            self.ind += 1
            if self.ind > len(Passes)-1:
                self.ind = 0
            currentpass = Passes[self.ind]
            print(currentpass)
            startpass = (currentpass.AOS - system.datetime0).total_seconds()
            tcapass = (currentpass.TCA - system.datetime0).total_seconds()
            endpass = (currentpass.LOS - system.datetime0).total_seconds()
            plot.set_alpha( [item>=startpass and item<=endpass for item in Times ])
            plt.suptitle(f'{spacecraft.name}\n{currentpass.TCA}')
            passTrack.ns.set_visible(False)
            passTrack.ns = ax.add_feature(Nightshade(currentpass.TCA, alpha=0.3))

            ax.set_title(f'Pass #{self.ind+1}/{len(Passes)}, Ground Radius: {text_radius} km.')

            startIndex = Times.index(startpass)
            endIndex   = Times.index(endpass)
            tcaIndex   = Times.index(tcapass)

            # startSpot.set_data([Longitudes[startIndex], Latitudes[startIndex]])
            # tcaSpot.set_data([Longitudes[tcaIndex], Latitudes[tcaIndex]])
            # endSpot.set_data([Longitudes[endIndex], Latitudes[endIndex]])
            # sun.set_data([SunLocation[tcaIndex].y, SunLocation[tcaIndex].x])

            startSpot.set_xdata([Longitudes[startIndex]])
            startSpot.set_ydata([Latitudes[startIndex]])

            tcaSpot.set_xdata([Longitudes[tcaIndex]])
            tcaSpot.set_ydata([Latitudes[tcaIndex]])

            endSpot.set_xdata([Longitudes[endIndex]])
            endSpot.set_ydata([Latitudes[endIndex]])

            sun.set_xdata([SunLocation[tcaIndex].y])
            sun.set_ydata([SunLocation[tcaIndex].x])

            lat1 = str('%.2F'% Latitudes[startIndex]+"°")
            lon1 = str('%.2F'% Longitudes[startIndex]+"°")
            alt1 = str('%.2F'% Altitudes[startIndex]+"km")
            txt1 = "lat: "+lat1+"\nlon: "+lon1+"\nalt: "+alt1
            label1.set(position=[Longitudes[startIndex], Latitudes[startIndex]], text=txt1)  

            lat2 = str('%.2F'% Latitudes[tcaIndex]+"°")
            lon2 = str('%.2F'% Longitudes[tcaIndex]+"°")
            alt2 = str('%.2F'% Altitudes[tcaIndex]+"km")
            elev = str('%.2F'% currentpass.angleTCA+"°")
            txt2 = "lat: "+lat2+"\nlon: "+lon2+"\nalt: "+alt2+"\nelev: "+elev
            label2.set(position=[Longitudes[tcaIndex], Latitudes[tcaIndex]], text=txt2)  

            lat3 = str('%.2F'% Latitudes[endIndex]+"°")
            lon3 = str('%.2F'% Longitudes[endIndex]+"°")
            alt3 = str('%.2F'% Altitudes[endIndex]+"km")
            txt3 = "lat: "+lat3+"\nlon: "+lon3+"\nalt: "+alt3
            label3.set(position=[Longitudes[endIndex], Latitudes[endIndex]], text=txt3)  

            plt.draw()

        def prev(self, event):
            global ns
            self.ind -= 1
            if self.ind < 0:
                self.ind = len(Passes)-1
            currentpass = Passes[self.ind]
            print(currentpass)
            startpass = (currentpass.AOS - system.datetime0).total_seconds()
            tcapass = (currentpass.TCA - system.datetime0).total_seconds()
            endpass = (currentpass.LOS - system.datetime0).total_seconds()
            plot.set_alpha( [item>=startpass and item<=endpass for item in Times ])
            plt.suptitle(f'{spacecraft.name}\n{currentpass.TCA}')
            passTrack.ns.set_visible(False)
            passTrack.ns = ax.add_feature(Nightshade(currentpass.TCA, alpha=0.3))
            
            ax.set_title(f'Pass #{self.ind+1}/{len(Passes)}, Ground Radius: {text_radius} km.')

            startIndex = Times.index(startpass)
            endIndex   = Times.index(endpass)
            tcaIndex   = Times.index(tcapass)

            # startSpot.set_data([Longitudes[startIndex], Latitudes[startIndex]])
            # tcaSpot.set_data([Longitudes[tcaIndex], Latitudes[tcaIndex]])
            # endSpot.set_data([Longitudes[endIndex], Latitudes[endIndex]])
            # sun.set_data([SunLocation[tcaIndex].y, SunLocation[tcaIndex].x])
            
            startSpot.set_xdata([Longitudes[startIndex]])
            startSpot.set_ydata([Latitudes[startIndex]])

            tcaSpot.set_xdata([Longitudes[tcaIndex]])
            tcaSpot.set_ydata([Latitudes[tcaIndex]])

            endSpot.set_xdata([Longitudes[endIndex]])
            endSpot.set_ydata([Latitudes[endIndex]])

            sun.set_xdata([SunLocation[tcaIndex].y])
            sun.set_ydata([SunLocation[tcaIndex].x])

            lat1 = str('%.2F'% Latitudes[startIndex]+"°")
            lon1 = str('%.2F'% Longitudes[startIndex]+"°")
            alt1 = str('%.2F'% Altitudes[startIndex]+"km")
            txt1 = "lat: "+lat1+"\nlon: "+lon1+"\nalt: "+alt1
            label1.set(position=[Longitudes[startIndex], Latitudes[startIndex]], text=txt1)  

            lat2 = str('%.2F'% Latitudes[tcaIndex]+"°")
            lon2 = str('%.2F'% Longitudes[tcaIndex]+"°")
            alt2 = str('%.2F'% Altitudes[tcaIndex]+"km")
            elev = str('%.2F'% currentpass.angleTCA+"°")
            txt2 = "lat: "+lat2+"\nlon: "+lon2+"\nalt: "+alt2+"\nelev: "+elev
            label2.set(position=[Longitudes[tcaIndex], Latitudes[tcaIndex]], text=txt2)  

            lat3 = str('%.2F'% Latitudes[endIndex]+"°")
            lon3 = str('%.2F'% Longitudes[endIndex]+"°")
            alt3 = str('%.2F'% Altitudes[endIndex]+"km")
            txt3 = "lat: "+lat3+"\nlon: "+lon3+"\nalt: "+alt3
            label3.set(position=[Longitudes[endIndex], Latitudes[endIndex]], text=txt3)  

            plt.draw()

    callback = Index()
    axprev = fig.add_axes([0.7, 0.05, 0.1, 0.075])
    axnext = fig.add_axes([0.81, 0.05, 0.1, 0.075])
    bnext = Button(axnext, 'Next')
    bnext.on_clicked(callback.next)
    bprev = Button(axprev, 'Previous')
    bprev.on_clicked(callback.prev)

    print("Number of Passes: "+str(len(Passes))+", Ground Radius: "+str(radius)+" m.")
    plt.show()

    return Passes

def animatedGroundTrack(recorder: Recorder, sample: int = 0, saveas: str = 'mp4', dpi: int = 300, filename='animatedGroundTrack'):

    # get datadict from recorder as dataframe
    df = pd.DataFrame.from_dict(recorder.dataDict)

    # variable for spacecraft and system
    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    if sample > 0:
        df1 = df.iloc[::sample,:]   
        df2 = df.iloc[df.index[-1]:,:]
        df1 = pd.concat([df1, df2], ignore_index=True, axis=0)
        
    elif sample == 0:
        df1 = df

    # split data columns from recorder into components
    SunLocation = [ item for item in df1['Sunlocation'].values.tolist()[:] ]
    Latitudes  = [ item[0] for item in df1['Location'].values.tolist()[:] ]
    Longitudes = [ item[1] for item in df1['Location'].values.tolist()[:] ]
    Altitudes  = [ item[2] for item in df1['Location'].values.tolist()[:] ]
    Datetimes  = [ item for item in df1['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df1['Datetime'][:] ]

    # initialize figure and projection 
    fig = plt.figure(figsize=(12, 6))
    ax  = plt.axes(projection=ccrs.PlateCarree())

    # globe projection image
    ax.stock_img()

    # nighshade 
    animatedGroundTrack.ns = ax.add_feature(Nightshade(system.datetime0, alpha=0.3))
    
    # gridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=1, color='white', alpha = 0.25,
                    linestyle='--')
    # labels on bottom and left axes
    gl.top_labels = False
    gl.right_labels = False
    # define the label style
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}
    # now we define exactly which ones to label and spruce up the labels
    gl.xlocator = mticker.FixedLocator([-180, -135, -90, -45, 0, 45, 90, 135, 180])
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xformatter = LONGITUDE_FORMATTER

    # create scatter plot of the ground track
    plot = plt.scatter(Longitudes, Latitudes,
        color='red', s=0.2, zorder=2.5,
        transform=ccrs.PlateCarree(),
        )
    
    # create a spot for the current track position
    spot, = ax.plot(Longitudes[0], Latitudes[0] , marker='o', color='white', markersize=12,
            alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)

    sun, = ax.plot(SunLocation[0].y, SunLocation[0].x , marker='o', color='yellow', markersize=12,
            alpha=1.0, transform=ccrs.PlateCarree(), zorder=3.0)

    # create legend / label on the current track position    
    geodetic_transform = ccrs.PlateCarree()._as_mpl_transform(ax)
    text_transform = offset_copy(geodetic_transform, units='dots', x=+15, y=+0)

    lat = str('%.2F'% Latitudes[0]+"°")
    lon = str('%.2F'% Longitudes[0]+"°")
    alt = str('%.2F'% Altitudes[0]+"km")
    txt = "lat: "+lat+"\nlon: "+lon+"\nlat: "+alt
    text = ax.text(Longitudes[0], Latitudes[0], txt,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=8,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})

    datetimeText = system.datetime0.strftime("%Y-%m-%d %H:%M:%S.%f")
    plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

    def init():
        return plot, spot, text, sun

    def update(frame):
        datetimeText = Datetimes[frame].strftime("%Y-%m-%d %H:%M:%S.%f")
        plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

        animatedGroundTrack.ns.set_visible(False)
        animatedGroundTrack.ns = ax.add_feature(Nightshade(Datetimes[frame], alpha=0.3))
        current_time = (Datetimes[frame] - system.datetime0).total_seconds()
        plot.set_alpha( [item <= current_time for item in Times ])

        index = len([ item for item in Times if item <= current_time ]) - 1
   
        # spot.set_data([Longitudes[index], Latitudes[index]])
        # sun.set_data([SunLocation[index].y, SunLocation[index].x])
        spot.set_xdata([Longitudes[index]])
        spot.set_ydata([Latitudes[index]])
        sun.set_xdata([SunLocation[index].y])
        sun.set_ydata([SunLocation[index].x])

        lat = str('%.2F'% Latitudes[index]+"°")
        lon = str('%.2F'% Longitudes[index]+"°")
        alt = str('%.2F'% Altitudes[index]+"km")
        txt = "lat: "+lat+"\nlon: "+lon+"\nalt: "+alt
        text.set(position=[Longitudes[index], Latitudes[index]], text=txt)       

        return plot, spot, text, sun

    print("\nRun Animation (from "+str(Times[0])+" to "+str(Times[-1])+", step="+str(Times[1]-Times[0])+")")
    anim = FuncAnimation(
        fig,
        update,
        frames = tqdm(np.arange(0, len(Times), 1), total=len(Times)-1,  position=0, desc='Animating Ground Track', bar_format='{l_bar}{bar:25}{r_bar}{bar:-25b}'),
        interval = 30
    )

    if saveas == "mp4":
        anim.save(filename+".mp4", writer='ffmpeg', fps=30, dpi=dpi)
    if saveas == "gif":
        anim.save(filename+".gif", writer='pillow', fps=30)

    plt.close()

def sensorTrack2(recorder: Recorder, sensor1: str, sensor2: str):
        
    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    df['Position']  = [ item.position for item in df['State'].values.tolist()[:] ]
    df['Velocity']  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    df['Quaternion'] = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    df['Bodyrate']  = [ item.bodyrate for item in df['State'].values.tolist()[:] ]

    Sensor1Data = [ item for item in df[sensor1].values.tolist()[:] ]
    Sensor2Data = [ item for item in df[sensor2].values.tolist()[:] ]
    Datetimes  = [ item for item in df['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    Sensor1X = [ item.x for item in Sensor1Data ]
    Sensor1Y = [ item.y for item in Sensor1Data ]
    Sensor1Z = [ item.z for item in Sensor1Data ]
    Sensor1M = [ item.magnitude() for item in Sensor1Data ]

    Sensor2X = [ item.x for item in Sensor2Data ]
    Sensor2Y = [ item.y for item in Sensor2Data ]
    Sensor2Z = [ item.z for item in Sensor2Data ]
    Sensor2M = [ item.magnitude() for item in Sensor2Data ]

    fig = plt.figure(figsize=(12,6))
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    ax4 = fig.add_subplot(2,2,4)

    ax1.plot(Times, Sensor1X, label='X', color='#1f77b4')
    ax2.plot(Times, Sensor1Y, label='Y', color='#ff7f0e')
    ax3.plot(Times, Sensor1Z, label='Z', color='#2ca02c')
    ax4.plot(Times, Sensor1M, label='Magnitude', color='#d62728')

    ax1.plot(Times, Sensor2X, label='X', color='#1f77b4', linestyle='--')
    ax2.plot(Times, Sensor2Y, label='Y', color='#ff7f0e', linestyle='--')
    ax3.plot(Times, Sensor2Z, label='Z', color='#2ca02c', linestyle='--')
    ax4.plot(Times, Sensor2M, label='Magnitude', color='#d62728', linestyle='--')


    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()

    ax1.set_title(f'X', fontsize=10)
    ax2.set_title(f'Y', fontsize=10)
    ax3.set_title(f'Z', fontsize=10)
    ax4.set_title(f'Magnitude', fontsize=10)

    ax2.set_xlabel("Time (s)")
    ax4.set_xlabel("Time (s)")

    plt.suptitle(f'{spacecraft.name}: {sensor1} vs {sensor2}\n{Datetimes[-1]}', fontname='monospace')
    plt.subplots_adjust(hspace=0.4)  

    cursor1 = Cursor(ax1, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor2 = Cursor(ax2, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor3 = Cursor(ax3, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor4 = Cursor(ax4, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')

    annot1 = ax1.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                         bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                         arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot2 = ax2.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                        bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                        arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot3 = ax3.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                        bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                        arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot4 = ax4.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                    bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                    arrowprops=dict(arrowstyle='-|>'), zorder=10)
    
    annot1.set_visible(False)
    annot2.set_visible(False)
    annot3.set_visible(False)
    annot4.set_visible(False)

    def axesToAnnot(axes):
        if axes == ax1:
            return annot1, Sensor1X, Sensor2X
        if axes == ax2:
            return annot2, Sensor1Y, Sensor2Y
        if axes == ax3:
            return annot3, Sensor1Z, Sensor2Z 
        if axes == ax4:
            return annot4, Sensor1M, Sensor2M 

    def onclick(event):
        if event.button == 1 and event.inaxes != None:
            x = event.xdata
            if x < 0:
                x = 0

            annot, func1, func2 = axesToAnnot(event.inaxes)
            filtered = [ time for time in Times if time <= x ]
            closestX = filtered[-1]
            closestY1 = func1[Times.index(closestX)]
            closestY2 = func2[Times.index(closestX)]

            annot.xy = (closestX, closestY1)    
            text = "(" + str( '%.2F'% closestX) + ", " + str( '%+.4E' % closestY1) + ", "+ str( '%+.4E' % closestY2) +")"
            annot.set_text(text)
            annot.set_visible(True)
            fig.canvas.draw()

            print("("+str(closestX)+", "+str(closestY1)+", "+str(closestY2)+")")

        elif event.button == 3 and event.inaxes != None:
            annot, func1, func2 = axesToAnnot(event.inaxes)
            annot.set_visible(False)
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

def sensorTrack(recorder: Recorder, sensor: str):
        
    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    df['Position']  = [ item.position for item in df['State'].values.tolist()[:] ]
    df['Velocity']  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    df['Quaternion'] = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    df['Bodyrate']  = [ item.bodyrate for item in df['State'].values.tolist()[:] ]

    SensorData = [ item for item in df[sensor].values.tolist()[:] ]
    Datetimes  = [ item for item in df['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    SensorX = [ item.x for item in SensorData ]
    SensorY = [ item.y for item in SensorData ]
    SensorZ = [ item.z for item in SensorData ]
    SensorM = [ item.magnitude() for item in SensorData ]

    fig = plt.figure(figsize=(12,6))
    ax1 = fig.add_subplot(2,2,1)
    ax2 = fig.add_subplot(2,2,2)
    ax3 = fig.add_subplot(2,2,3)
    ax4 = fig.add_subplot(2,2,4)

    ax1.plot(Times, SensorX, label='X', color='#1f77b4')
    ax2.plot(Times, SensorY, label='Y', color='#ff7f0e')
    ax3.plot(Times, SensorZ, label='Z', color='#2ca02c')
    ax4.plot(Times, SensorM, label='Magnitude', color='#d62728')

    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()

    ax1.set_title(f'X', fontsize=10)
    ax2.set_title(f'Y', fontsize=10)
    ax3.set_title(f'Z', fontsize=10)
    ax4.set_title(f'Magnitude', fontsize=10)

    ax2.set_xlabel("Time (s)")
    ax4.set_xlabel("Time (s)")

    plt.suptitle(f'{spacecraft.name}: {sensor}\n{Datetimes[-1]}', fontname='monospace')
    plt.subplots_adjust(hspace=0.4)  

    cursor1 = Cursor(ax1, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor2 = Cursor(ax2, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor3 = Cursor(ax3, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')
    cursor4 = Cursor(ax4, horizOn=True, vertOn=True, useblit=True, color='gray',linewidth=1, linestyle='--')

    annot1 = ax1.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                         bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                         arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot2 = ax2.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                        bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                        arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot3 = ax3.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                        bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                        arrowprops=dict(arrowstyle='-|>'), zorder=10)
    annot4 = ax4.annotate("", xy=(0,0), xytext=(-40,40), textcoords="offset points",
                    bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1),
                    arrowprops=dict(arrowstyle='-|>'), zorder=10)
    
    annot1.set_visible(False)
    annot2.set_visible(False)
    annot3.set_visible(False)
    annot4.set_visible(False)

    def axesToAnnot(axes):
        if axes == ax1:
            return annot1, SensorX
        if axes == ax2:
            return annot2, SensorY
        if axes == ax3:
            return annot3, SensorZ
        if axes == ax4:
            return annot4, SensorM

    def onclick(event):
        if event.button == 1 and event.inaxes != None:
            x = event.xdata
            if x < 0:
                x = 0

            annot, func = axesToAnnot(event.inaxes)
            filtered = [ time for time in Times if time <= x ]
            closestX = filtered[-1]
            closestY = func[Times.index(closestX)]

            annot.xy = (closestX, closestY)    
            text = "(" + str( '%.2F'% closestX) + ", " + str( '%+.4E' % closestY) +")"
            annot.set_text(text)
            annot.set_visible(True)
            fig.canvas.draw()

            print("("+str(closestX)+", "+str(closestY)+")")

        elif event.button == 3 and event.inaxes != None:
            annot, func = axesToAnnot(event.inaxes)
            annot.set_visible(False)
            fig.canvas.draw()
    
    fig.canvas.mpl_connect('button_press_event', onclick)

    plt.show()

def sensorTrack0(recorder: Recorder, sensor: str, args=[1]):
        
    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    df['Position']  = [ item.position for item in df['State'].values.tolist()[:] ]
    df['Velocity']  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    df['Quaternion'] = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    df['Bodyrate']  = [ item.bodyrate for item in df['State'].values.tolist()[:] ]

    SensorData = [ item for item in df[sensor].values.tolist()[:] ]
    Datetimes  = [ item for item in df['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    fig = plt.figure(figsize=(12,6))
    ax = fig.add_subplot(1,1,1)

    if isinstance(SensorData[0], Vector):
        SensorX = [ item.x*args[0] for item in SensorData ]
        SensorY = [ item.y*args[0] for item in SensorData ]
        SensorZ = [ item.z*args[0] for item in SensorData ]
        SensorM = [ item.magnitude()*args[0] for item in SensorData ]

        ax.plot(Times, SensorX, label='X', color='#1f77b4')
        ax.plot(Times, SensorY, label='Y', color='#ff7f0e')
        ax.plot(Times, SensorZ, label='Z', color='#2ca02c')
        ax.plot(Times, SensorM, label='Magnitude', color='#d62728')

    elif isinstance(SensorData[0], (int, float)):

        ax.plot(Times, SensorData, label='Magnitude', color='#d62728')

    ax.grid()
    ax.set_xlabel("Time (s)")
    ax.legend()

    plt.suptitle(f'{spacecraft.name}: {sensor}\n{Datetimes[-1]}', fontname='monospace')

    plt.show()

def animatedSensorTrack(recorder: Recorder, sensor: str, sample: int = 0, saveas: str = 'mp4', dpi: int = 300, filename='SensorTrack'):

    # get datadict from recorder as dataframe
    df = pd.DataFrame.from_dict(recorder.dataDict)

    # variable for spacecraft and system
    spacecraft = recorder.attachedTo
    system     = spacecraft.system

    df['Position']  = [ item.position for item in df['State'].values.tolist()[:] ]
    df['Velocity']  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    df['Quaternion'] = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    df['Bodyrate']  = [ item.bodyrate for item in df['State'].values.tolist()[:] ]

    if sample > 0:
        df1 = df.iloc[::sample,:]   
        df2 = df.iloc[df.index[-1]:,:]
        df1 = pd.concat([df1, df2], ignore_index=True, axis=0)

    elif sample == 0:
        df1 = df

    # split data columns from recorder into components
    SunLocation = [ item for item in df1['Sunlocation'].values.tolist()[:] ]
    SensorData = [ item for item in df1[sensor].values.tolist()[:] ]
    Latitudes  = [ item[0] for item in df1['Location'].values.tolist()[:] ]
    Longitudes = [ item[1] for item in df1['Location'].values.tolist()[:] ]
    Altitudes  = [ item[2] for item in df1['Location'].values.tolist()[:] ]
    Datetimes  = [ item for item in df1['Datetime'] ][:]
    Times      = [ (item - system.datetime0).total_seconds() for item in df1['Datetime'][:] ]

    SensorX = [ item.x for item in SensorData ]
    SensorY = [ item.y for item in SensorData ]
    SensorZ = [ item.z for item in SensorData ]

    # initialize figure and projection 
    # plt.style.use("seaborn-v0_8")
    fig = plt.figure(figsize=(12, 9))
    fig.tight_layout()
    gs = gridspec.GridSpec(2,1, height_ratios=[2, 1])
    ax1 = plt.subplot(gs[0], projection=ccrs.PlateCarree())
    ax2 = plt.subplot(gs[1])
    # ax1 = fig.add_subplot(3,1,1, height_ratio = 2, projection=ccrs.PlateCarree())
    # ax2 = fig.add_subplot(3,1,3)

    # globe projection image
    ax1.stock_img()

    # nighshade 
    animatedGroundTrack.ns = ax1.add_feature(Nightshade(system.datetime0, alpha=0.3))
    
    # gridlines
    gl = ax1.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=1, color='white', alpha = 0.25,
                    linestyle='--')
    # labels on bottom and left axes
    gl.top_labels = False
    gl.right_labels = False
    # define the label style
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}
    # now we define exactly which ones to label and spruce up the labels
    gl.xlocator = mticker.FixedLocator([-180, -135, -90, -45, 0, 45, 90, 135, 180])
    gl.ylocator = mticker.FixedLocator([-80, -60, -40, -20, 0, 20, 40, 60, 80])
    gl.xformatter = LONGITUDE_FORMATTER

    # create scatter plot of the ground track
    plot = ax1.scatter(Longitudes, Latitudes,
        color='red', s=0.2, zorder=2.5,
        transform=ccrs.PlateCarree(),
        )
    
    ln1, = ax2.plot([],[], label="X")
    ln2, = ax2.plot([],[], label="Y")
    ln3, = ax2.plot([],[], label="Z")

    # create a spot for the current track position
    spot, = ax1.plot(Longitudes[0], Latitudes[0] , marker='o', color='white', markersize=12,
            alpha=0.5, transform=ccrs.PlateCarree(), zorder=3.0)
    
    sun, = ax1.plot(SunLocation[0].y, SunLocation[0].x , marker='o', color='yellow', markersize=12,
            alpha=1.0, transform=ccrs.PlateCarree(), zorder=3.0)

    # create legend / label on the current track position    
    geodetic_transform = ccrs.PlateCarree()._as_mpl_transform(ax1)
    text_transform = offset_copy(geodetic_transform, units='dots', x=+15, y=+0)

    lat = str('%.2F'% Latitudes[0]+"°")
    lon = str('%.2F'% Longitudes[0]+"°")
    alt = str('%.2F'% Altitudes[0]+"km")
    txt = "lat: "+lat+"\nlon: "+lon+"\nlat: "+alt
    text = ax1.text(Longitudes[0], Latitudes[0], txt,
        verticalalignment='center', horizontalalignment='left',
        transform=text_transform, fontsize=8,
        bbox=dict(facecolor='white', alpha=0.5, boxstyle='round'), fontdict={'family':'monospace'})

    datetimeText = system.datetime0.strftime("%Y-%m-%d %H:%M:%S.%f")
    plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

    ax2.title.set_text(f'{sensor} output')
    ax2.grid(visible=True)

    def init():

        plt.subplots_adjust(wspace=0, right=0, left=0)   

        return plot, spot, text, ln1, ln2, ln3, sun

    def update(frame):
        datetimeText = Datetimes[frame].strftime("%Y-%m-%d %H:%M:%S.%f")
        plt.suptitle(f'{spacecraft.name}\n{datetimeText}', fontname='monospace')

        animatedGroundTrack.ns.set_visible(False)
        animatedGroundTrack.ns = ax1.add_feature(Nightshade(Datetimes[frame], alpha=0.3))
        current_time = (Datetimes[frame] - system.datetime0).total_seconds()
        plot.set_alpha( [item <= current_time for item in Times ])

        ln1.set_data(Times[0: frame], SensorX[0: frame])
        ln2.set_data(Times[0: frame], SensorY[0: frame])
        ln3.set_data(Times[0: frame], SensorZ[0: frame])

        ln1.set_label("X = "+str('%+.3E' % SensorX[frame]))
        ln2.set_label("Y = "+str('%+.3E' % SensorY[frame]))
        ln3.set_label('Z = '+str('%+.3E' % SensorZ[frame]))
        ax2.legend(loc='lower left', prop={'family':'monospace'}, ncol=3)

        index = len([ item for item in Times if item <= current_time ]) - 1
   
        # spot.set_data([Longitudes[index], Latitudes[index]])
        # sun.set_data([SunLocation[index].y, SunLocation[index].x])
        spot.set_xdata([Longitudes[index]])
        spot.set_ydata([Latitudes[index]])
        sun.set_xdata([SunLocation[index].y])
        sun.set_ydata([SunLocation[index].x])
        

        lat = str('%.2F'% Latitudes[index]+"°")
        lon = str('%.2F'% Longitudes[index]+"°")
        alt = str('%.2F'% Altitudes[index]+"km")
        txt = "lat: "+lat+"\nlon: "+lon+"\nalt: "+alt
        text.set(position=[Longitudes[index], Latitudes[index]], text=txt)   

        if frame > 0:
            maxV = 0
            for rate in SensorData[0: frame]:
                lis = abs(np.array([rate.x, rate.y, rate.z]))
                if max(lis) > maxV:
                    maxV = max(lis)
            if maxV != 0:
                ax2.set_ylim(-1.5*maxV,1.5*maxV)

        ax2.set_xlim(Times[0]-1, Times[frame]+10)    

        return plot, spot, text, ln1, ln2, ln3, sun

    print("\nRun Animation (from "+str(Times[0])+" to "+str(Times[-1])+", step="+str(Times[1]-Times[0])+")")
    anim = FuncAnimation(
        fig,
        update,
        frames = tqdm(np.arange(0, len(Times), 1), total=len(Times)-1,  position=0, desc='Animating Sensor Track', bar_format='{l_bar}{bar:25}{r_bar}{bar:-25b}'),
        interval = 30
    )

    if saveas == "mp4":
        anim.save(filename+".mp4", writer='ffmpeg', fps=30, dpi=dpi)
    if saveas == "gif":
        anim.save(filename+".gif", writer='pillow', fps=30)

    plt.close()

def export(recorder: Recorder, tStart: int = 0, tEnd: int = -1, filename='simdata'):

    n      = 4
    method = 'linear'
    order  = 5

    df = pd.DataFrame.from_dict(recorder.dataDict)

    spacecraft = recorder.attachedTo
    system = spacecraft.system

    Positions   = [ item.position for item in df['State'].values.tolist()[:] ]
    Velocities  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    Quaternions = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    Bodyrates   = [ item.bodyrate for item in df['State'].values.tolist()[:] ]
    Datetimes   = [ item for item in df['Datetime'] ][:]
    Times       = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    if tEnd < 0:
        tEnd = Times[-1]

    out = pd.DataFrame()

    out['t'] = pd.DataFrame( Times )
    out['x'] = pd.DataFrame( [ item.x for item in Positions ] )
    out['y'] = pd.DataFrame( [ item.y for item in Positions ] )
    out['z'] = pd.DataFrame( [ item.z for item in Positions ] )
    out['xdot'] = pd.DataFrame( [ item.x for item in Velocities ] )
    out['ydot'] = pd.DataFrame( [ item.y for item in Velocities ] )
    out['zdot'] = pd.DataFrame( [ item.z for item in Velocities ] )
    out['q0'] = pd.DataFrame( [ item.w for item in Quaternions ] )
    out['q1'] = pd.DataFrame( [ item.x for item in Quaternions ] )
    out['q2'] = pd.DataFrame( [ item.y for item in Quaternions ] )
    out['q3'] = pd.DataFrame( [ item.z for item in Quaternions ] )
    out['p'] = pd.DataFrame( [ item.x for item in Bodyrates ] )
    out['q'] = pd.DataFrame( [ item.y for item in Bodyrates ] )
    out['r'] = pd.DataFrame( [ item.z for item in Bodyrates ] )
    
    outcopy = out.copy()

    new_index = outcopy.index
    new_out = outcopy.copy()

    new_out['index'] = new_index*n
    new_out = new_out.set_index('index')

    new_index2 = pd.RangeIndex(start=0, stop=(len(new_index)*n)-(n-1), step=1)
    new_out = new_out.reindex(new_index2)

    new_out = new_out.interpolate(method=method, order=order)
    
    clipped_out = new_out[new_out['t']>=tStart]
    clipped_out = clipped_out[clipped_out['t']<=tEnd]
    
    clipped_out.to_csv(filename+".csv",index=False)

    print("\n\t"+"Filename: "+filename+".csv EXPORTED!")

def exportALL(recorder: Recorder, tStart: int = 0, tEnd: int = -1, filename='data'):

    n      = 4
    method = 'linear'
    order  = 5

    df = pd.DataFrame.from_dict(recorder.dataDict)

    # spacecraft = recorder.attachedTo
    # system = spacecraft.system

    Positions   = [ item.position for item in df['State'].values.tolist()[:] ]
    Velocities  = [ item.velocity for item in df['State'].values.tolist()[:] ]
    Quaternions = [ item.quaternion for item in df['State'].values.tolist()[:] ]
    Bodyrates   = [ item.bodyrate for item in df['State'].values.tolist()[:] ]
    Location    = [ item for item in df['Location'].values.tolist()[:] ]
    Netforce    = [ item for item in df['Netforce'].values.tolist()[:] ]
    Nettorque   = [ item for item in df['Nettorque'].values.tolist()[:] ]
    Netmoment   = [ item for item in df['Netmoment'].values.tolist()[:] ]
    Sunlocation = [ item for item in df['Sunlocation'].values.tolist()[:] ]
    SpAngMom    = [ item for item in df['SpecificAngularMomentum'] ]
    SpMechEn    = [ item for item in df['SpecificMechanicalEnergy'] ]
    BdAngMom    = [ item for item in df['BodyAngularMomentum'] ]

    dataset = []
    for col in df.columns[10:]:
        if isinstance(df[col][0], Vector):
            dataset.append( [ item for item in df[col].values.tolist()[:] ] )
        if isinstance(df[col][0], (int, float)):
            dataset.append( [ item for item in df[col] ] )

    # Datetimes   = [ item for item in df['Datetime'] ][:]
    # Times       = [ (item - system.datetime0).total_seconds() for item in df['Datetime'][:] ]

    # if tEnd < 0:
    #     tEnd = Times[-1]

    # out = pd.DataFrame()

    datalines = []
    dt = ''.join(e for e in str(datetime.datetime.now()) if e.isalnum())
    with open(filename+'_'+dt+".txt",'w') as outfile:

        outfile.write( "UNIXTIME\nYEAR\nMONTH\nDAY\nHOUR\nMINUTE\nSECOND\nMICROSECOND\n" + \
            "POSITION(X, m)\nPOSITION(Y, m)\nPOSITION(Z, m)\n" + \
            "VELOCITY(X, m/s)\nVELOCITY(Y, m/s)\nVELOCITY(Z, m/s)\n" + \
            "QUATERNON(W, real)\nQUATERNION(X)\nQUATERNION(Y)\nQUATERNION(Z)\n" + \
            "BODYRATE(X, roll, rad/s)\nBODYRATE(Y, pitch, rad/s)\nBODYRATE(Z, yaw, rad/s)\n" + \
            "LOCATION(latitude, deg)\nLOCATION(longitude, deg)\nLOCATION(altitude, km)\n" + \
            "NETFORCE(X, N)\nNETFORCE(Y, N)\nNETFORCE(Z,N)\n" + \
            "NETMOMENT(X, kgm^2/s)\nNETMOMENT(Y, kgm^2/s)\nNETMOMENT(Z, kgm^2/s)\n" + \
            "SUNLOCATION(latitude, deg)\nSUNLOCATION(longitude, deg)\nSUNLOCATION(unused)\n" + \
            "SPECIFICANGULARMOMENTUM( m^2/s )\n" + \
            "SPECIFICMECHANICALENERGY( m^2/s^2 )\n" + \
            "BODYANGULARMOMENTUM( kgm^2/s )\n" )
        
        for col in df.columns[10:]:
            outfile.write(col+"\n")

        for i in np.arange(0,len(df),1):
            unixTime = int(calendar.timegm(df['Datetime'][i].utctimetuple()))
            unixValue = f'{unixTime}'
            dateValue = df['Datetime'][i].strftime('%Y, %m, %d, %H, %M, %S, %f')
            positionValue = f'{Positions[i].x:.15f}, {Positions[i].y:.15f}, {Positions[i].z:.15f}'
            velocityValue = f'{Velocities[i].x:.15f}, {Velocities[i].y:.15f}, {Velocities[i].z:.15f}'
            quaternionValue = f'{Quaternions[i].w:.15f}, {Quaternions[i].x:.15f}, {Quaternions[i].y:.15f}, {Quaternions[i].z:.15f}'
            bodyrateValue = f'{Bodyrates[i].x:.15f}, {Bodyrates[i].y:.15f}, {Bodyrates[i].z:.15f}'
            locationValue = f'{Location[i].x:.15f}, {Location[i].y:.15f}, {Location[i].z:.15f}'
            netforceValue = f'{Netforce[i].x:.15f}, {Netforce[i].y:.15f}, {Netforce[i].z:.15f}'
            nettorqueValue = f'{Nettorque[i].x:.15f}, {Nettorque[i].y:.15f}, {Nettorque[i].z:.15f}'
            netmomentValue = f'{Netmoment[i].x:.15f}, {Netmoment[i].y:.15f}, {Netmoment[i].z:.15f}'
            sunlocationValue = f'{Sunlocation[i].x:.15f}, {Sunlocation[i].y:.15f}, {Sunlocation[i].z:.15f}'
            samValue = f'{SpAngMom[i]:.15f}'
            smeValue = f'{SpMechEn[i]:.15f}'
            bamValue = f'{BdAngMom[i]:.15f}'

            dataValues = []
            for icol in np.arange(0, len(df.columns[10:]), 1):
                if isinstance(df[col][0], Vector):
                    dataValues.append( f'{dataset[icol][i].x:.15f}, {dataset[icol][i].y:.15f}, {dataset[icol][i].z:.15f}' )
                if isinstance(df[col][0], (int, float)):
                    dataValues.append( [ f'{dataset[icol][i]:.15f}' ] )


            sep = ", "

            dataline = unixValue + sep + dateValue + sep + positionValue + sep + velocityValue + sep + quaternionValue + sep + bodyrateValue  + sep + \
                locationValue + sep +netforceValue + sep + nettorqueValue + sep + netmomentValue + sep + sunlocationValue + sep + \
                samValue + sep + smeValue + sep + bamValue
            
            for icol in np.arange(0, len(df.columns[10:]), 1):
                dataline = dataline + sep + dataValues[icol]
            outfile.write(dataline+'\n')

    print("\n\t"+"Filename: "+filename+'_'+dt+".txt EXPORTED!")