from leoss import *
import pickle

system = LEOSS()

def gyrofunction(spacecraft, args):
    gyro_bodyrate = Vector(0,0,0)
    if len(spacecraft.recorder['State']) > args[0]:
        gyro_bodyrate = spacecraft.recorder['State'][-args[0]].bodyrate
    return gyro_bodyrate

def gpsfunction(spacecraft, args):
    gps_position = Vector(0,0,0)
    if len(spacecraft.recorder['Location']) > args[0]:
        gps_position = spacecraft.recorder['Location'][-args[0]]
    return gps_position

def mtmfunction(spacecraft, args):
    if len(spacecraft.recorder['Location']) > args[0] and spacecraft.recorder['Location'][-args[0]].magnitude != 0:
        location = spacecraft.recorder['Location'][-args[0]]
        magfield = IGRF.igrf_value(location[0], location[1], location[2], spacecraft.recorder['Datetime'][-args[0]].year)[3:6]
        magfield_NED_vector = Vector(magfield[0], magfield[1], magfield[2]) * 1e-9

        position = spacecraft.recorder['State'][-args[0]].position
        R = position.magnitude()
        theta = math.acos(position.z/R)
        psi   = math.atan2(position.y, position.x)
        RPY = Vector(0, (theta+math.pi)*R2D, psi*R2D)

        magfield_inertial_vector = RPY.RPY_toYPR_quaternion().toMatrix().transpose()*magfield_NED_vector

        quaternion = spacecraft.recorder['State'][-args[0]].quaternion
        magfield_body_vector = quaternion.toMatrix()*magfield_inertial_vector
    else:
        magfield_body_vector = Vector(0,0,0)

    return magfield_body_vector

def bdotctrlfunction(spacecraft: Spacecraft, args):
    magfield_body_vector0 = Vector(0,0,0)
    time0 = spacecraft.system.datetime0

    control_moment = Vector(0,0,0)

    if len(spacecraft.recorder[args[1]]) > 2:
        magfield_body_vector0 = spacecraft.recorder[args[1]][-1]
        time0 = spacecraft.recorder['Datetime'][-1]

    if len(spacecraft.recorder[args[1]]) > 1:
        magfield_body_vector = spacecraft[args[1]]
        time = spacecraft.system.datenow()
        
        delta_magfield_body_vector = magfield_body_vector - magfield_body_vector0
        delta_time = (time - time0).total_seconds()

        control_moment = -args[0] * (delta_magfield_body_vector/delta_time)

    return control_moment

def mtqfunction(spacecraft: Spacecraft, args):
    
    control_moment = spacecraft[args[0]]
    magfield_body_vector = spacecraft['ideal_MTM']
    control_torque = control_moment.cross(magfield_body_vector)

    return control_torque
    

with open('system_MULA.pkl','rb') as inp:
    system = pickle.load(inp)

spacecraft = system.getSpacecrafts()
recorder   = system.getRecorders()

# sensorTrack2(recorder['DIWATA'], 'gyro','Bodyrate')
# sensorTrack2(recorder['DIWATA'] ,'mtm','ideal_MTM')
# exportALL(recorder['MULA'])
export(recorder['MULA'])
# sensorTrack0(recorder['DIWATA'], 'Bodyrate',[R2D])
# sensorTrack0(recorder['MULA'], 'Bodyrate',[R2D])
# animatedAttitudeTrack(recorder["DIWATA"], frameRef='Orbit', sample=50, saveas='mp4')

