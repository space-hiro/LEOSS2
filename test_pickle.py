from leoss import *
import pickle

system = LEOSS()

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

