import datetime
import calendar
import math
import time as clock

from tqdm import tqdm
import pyIGRF as IGRF

R2D = 180/math.pi
D2R = math.pi/180

class Vector():

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'Vector({self.x}, {self.y}, {self.z})'
    
    def __str__(self):
        return f'Vector({self.x}, {self.y}, {self.z})'
    
    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z
        else:
            raise IndexError("There are only three elements in the vector")
        
    def __add__(self, other):
        if isinstance(other, Vector):
            return Vector(
                self.x + other.x,
                self.y + other.y,
                self.z + other.z
                )
        else:
            raise TypeError("Operand must a Vector")
    
    def __sub__(self, other):
        if isinstance(other, Vector):
            return Vector(
                self.x - other.x,
                self.y - other.y,
                self.z - other.z
                )
        else:
            raise TypeError("Operand must a Vector")
    
    def __mul__(self, other):
        if isinstance(other, Vector):
            return Vector(
                self.x * other.x,
                self.y * other.y,
                self.z * other.z
                )
        elif isinstance(other, (int, float)):
            return Vector(
                self.x * other,
                self.y * other,
                self.z * other
                )
        else:
            raise TypeError("Operand must be Vector, int, or float")
        
    def __rmul__(self, other):
        return self * other
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector(
                self.x / other,
                self.y / other,
                self.z / other
                )
        else:
            raise TypeError("Operand must be int, or float")
        
    def __eq__(self, other):
        if isinstance(other, Vector):
            return (self.x == other.x and self.y == other.y and self.z == other.z)
        else:
            raise TypeError("Operand must be Vector")
        
    def cross(self, other):
        if isinstance(other, Vector):
            return Vector(
                self.y * other.z - self.z * other.y,
                self.z * other.x - self.x * other.z,
                self.x * other.y - self.y * other.x
                )
        else:
            raise TypeError("Operand must be Vector")

    def magnitude(self):
        return (self.x**2 + self.y**2 + self.z**2)**0.5
    
    def normalize(self):
        magnitude = self.magnitude()
        return Vector(
            self.x / magnitude,
            self.y / magnitude,
            self.z / magnitude
        )

    def sum(self):
        return self.x + self.y +self.z

    def RPY_toYPR_quaternion(self, unit='deg'):
        if unit == 'deg':
            self.x = self.x * D2R
            self.y = self.y * D2R
            self.z = self.z * D2R
            unit = 'rad'
        if unit == 'rad':
            phi   = self.x
            theta = self.y
            psi   = self.z
            qW = math.cos(phi/2)*math.cos(theta/2)*math.cos(psi/2) + math.sin(phi/2)*math.sin(theta/2)*math.sin(psi/2)
            qX = math.sin(phi/2)*math.cos(theta/2)*math.cos(psi/2) - math.cos(phi/2)*math.sin(theta/2)*math.sin(psi/2)
            qY = math.cos(phi/2)*math.sin(theta/2)*math.cos(psi/2) + math.sin(phi/2)*math.cos(theta/2)*math.sin(psi/2)
            qZ = math.cos(phi/2)*math.cos(theta/2)*math.sin(psi/2) - math.sin(phi/2)*math.sin(theta/2)*math.cos(psi/2)
            return Quaternion(qW, qX, qY, qZ)
        else:
            raise ValueError("Unit should be either 'deg' or rad'")

    def __len__(self):
        return 3

class Matrix():

    def __init__(self, x=Vector(1,0,0), y=Vector(0,1,0), z=Vector(0,0,1)):
        self.x = x
        self.y = y
        self.z = z
        self.xx = x.x; self.yx = y.x; self.zx = z.x
        self.xy = x.y; self.yy = y.y; self.zy = z.y
        self.xz = x.z; self.yz = y.z; self.zz = z.z
    
    def __repr__(self):
        return f'Matrix({self.xx}, {self.yx}, {self.zx}; {self.xy}, {self.yy}, {self.zy}; {self.xz}, {self.yz}, {self.zz})'
    
    def __str__(self):
        return f'Matrix({self.xx}, {self.yx}, {self.zx}; {self.xy}, {self.yy}, {self.zy}; {self.xz}, {self.yz}, {self.zz})'

    def transpose(self):
        x = Vector(self.xx, self.yx, self.zx)
        y = Vector(self.xy, self.yy, self.zy)
        z = Vector(self.xz, self.yz, self.zz)
        return Matrix(x, y, z)

    def __mul__(self, other):
        if isinstance(other, Vector):
            T = self.transpose()
            x = (T.x * other).sum()
            y = (T.y * other).sum()
            z = (T.z * other).sum()
            return Vector(x, y, z)
        elif isinstance(other, Matrix):
            x = self * other.x
            y = self * other.y
            z = self * other.z
            return Matrix(x, y, z)
        elif isinstance(other, int) or isinstance(other, float):
            return Matrix(self.x*other, self.y*other, self.z*other)
        else:
            raise TypeError("Operand should be a Vector, int or float")
        
    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Matrix(self.x*other, self.y*other, self.z*other)
        else:
            raise TypeError("Operand should be int or float")

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Matrix(self.x/other, self.y/other, self.z/other)
        else:
            raise TypeError("Operand should be int or float")

    def trace(self):
        return self.xx + self.yy + self.zz 

    def inverse(self):
        m1 = self.xx; m2 = self.yx; m3 = self.zx
        m4 = self.xy; m5 = self.yy; m6 = self.zy
        m7 = self.xz; m8 = self.yz; m9 = self.zz
        
        x = Vector( m5*m9-m6*m8, m6*m7-m4*m9, m4*m8-m5*m7 )
        y = Vector( m3*m8-m2*m9, m1*m9-m3*m7, m2*m7-m1*m8 )
        z = Vector( m2*m6-m3*m5, m3*m4-m1*m6, m1*m5-m2*m4 )
        inv = Matrix(x, y, z)

        w = Vector(inv.xx, inv.yx, inv.zx)
        return inv / (w*self.x).sum()

    def isOrthogonal(self):
        I = self * self.transpose()
        return ( abs(I.trace() - 3.00) <= 1e-3)

    def toQuaternion(self):
        if self.isOrthogonal() == False:
            raise ValueError("Matrix is not Orthogonal")
        else:
            B = []
            B.append(0.25*(1+self.trace()))
            B.append(0.25*(1+2*self.xx-self.trace()))
            B.append(0.25*(1+2*self.yy-self.trace()))
            B.append(0.25*(1+2*self.zz-self.trace()))

            B0B1 = 0.25*( self.zy-self.yz )
            B0B2 = 0.25*( self.xz-self.zx )
            B0B3 = 0.25*( self.yx-self.xy )
            B2B3 = 0.25*( self.zy+self.yz )
            B3B1 = 0.25*( self.xz+self.zx )
            B1B2 = 0.25*( self.yx+self.xy )
            
            b = [math.sqrt(item) for item in B]
            Q = Quaternion()

            if B[0] == max(B):
                Q.w = b[0]
                Q.x = B0B1/b[0]
                Q.y = B0B2/b[0]
                Q.z = B0B3/b[0]
            elif B[1] == max(B):
                Q.w = B0B1/b[1]
                Q.x = b[1]
                Q.y = B1B2/b[1]
                Q.z = B3B1/b[1]
            elif B[2] == max(B):
                Q.w = B0B2/b[2]
                Q.x = B1B2/b[2]
                Q.y = b[2]
                Q.z = B2B3/b[2]
            elif B[3] == max(B):
                Q.w = B0B3/b[3]
                Q.x = B3B1/b[3]
                Q.y = B2B3/b[3]
                Q.z = b[3]
            return Q

class Quaternion():

    def __init__(self, w=1.0, x=0.0, y=0.0, z=0.0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'Quaternion({self.w}, {self.x}, {self.y}, {self.z})'
    
    def __str__(self):
        return f'Quaternion({self.w}, {self.x}, {self.y}, {self.z})'
    
    def __getitem__(self, item):
        if item == 0:
            return self.w
        elif item == 1:
            return self.x
        elif item == 2:
            return self.y
        elif item == 3:
            return self.z
        else:
            raise IndexError("There are only four elements in the quaternion")
        
    def __add__(self, other):
        if isinstance(other, Quaternion):
            q = Quaternion(
                other.w * self.w - other.x * self.x - other.y * self.y - other.z * self.z,
                other.x * self.w + other.w * self.x + other.z * self.y - other.y * self.z,
                other.y * self.w - other.z * self.x + other.w * self.y + other.x * self.z,
                other.z * self.w + other.y * self.x - other.x * self.y + other.w * self.z
                )
            return q.normalize()
        else:
            raise TypeError("Operand must a Quaternion")
    
    def __sub__(self, other):
        if isinstance(other, Quaternion):
            return Quaternion(
                 other.w * self.w + other.x * self.x + other.y * self.y + other.z * self.z,
                -other.x * self.w + other.w * self.x + other.z * self.y - other.y * self.z,
                -other.y * self.w - other.z * self.x + other.w * self.y + other.x * self.z,
                -other.z * self.w + other.y * self.x - other.x * self.y + other.w * self.z
                ).normalize()
        else:
            raise TypeError("Operand must a Quaternion")
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Quaternion(
                self.w * other,
                self.x * other,
                self.y * other,
                self.z * other
                )
        else:
            raise TypeError("Operand must be Quaternion, int, or float")
        
    def __rmul__(self, other):
        return self * other
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Quaternion(
                self.w / other,
                self.x / other,
                self.y / other,
                self.z / other
                )
        else:
            raise TypeError("Operand must be int, or float")
        
    def __eq__(self, other):
        if isinstance(other, Quaternion):
            if (self.w == other.w and self.x == other.x and self.y == other.y and self.z == other.z):
                return True
            elif abs((self-other).angle()*R2D) < 1e-8:
                return True
            else:
                return False
        else:
            raise TypeError("Operand must be Quaternion")

    def magnitude(self):
        return (self.w**2 + self.x**2 + self.y**2 + self.z**2)**0.5
    
    def normalize(self):
        magnitude = self.magnitude()
        return Quaternion(
            self.w / magnitude,
            self.x / magnitude,
            self.y / magnitude,
            self.z / magnitude
        )
    
    def vector(self):
        return Vector(self.x, self.y, self.z)
    
    def angle(self):
        return 2*math.acos(self.w)
    
    def toMRP(self):
        return Vector(self.x, self.y, self.z) / (1 + self.magnitude())

    def toMatrix(self):
        x = Vector()
        y = Vector()
        z = Vector()
        x.x = 1 - 2*(self.y**2 + self.z**2)
        y.x = 2*self.x*self.y + 2*self.w*self.z
        z.x = -2*self.w*self.y + 2*self.x*self.z

        x.y = 2*self.x*self.y - 2*self.w*self.z
        y.y = 1 - 2*(self.x**2+self.z**2)
        z.y = 2*self.w*self.x + 2*self.y*self.z
        
        x.z = 2*self.w*self.y + 2*self.x*self.z
        y.z = -2*self.w*self.x + 2*self.y*self.z
        z.z = 1 - 2*(self.x**2 + self.y**2)
        return Matrix(x, y, z)

    def YPR_toRPY_vector(self):
        Q = self.normalize()

        phi   = math.atan2(2*(Q.w*Q.x + Q.y*Q.z),1-2*(Q.x**2 + Q.y**2))
        theta = math.asin(2*(Q.w*Q.y-Q.z*Q.x))
        psi   = math.atan2(2*(Q.w*Q.z + Q.x*Q.y),1-2*(Q.y**2 + Q.z**2))

        return Vector(phi, theta, psi)
    
    def rotate(self, other: Vector):
        if isinstance(other, Vector):
            Rt = Quaternion(self.w, -self.x, -self.y, -self.z)
            P  = Quaternion(0, other.x, other.y, other.z)
            RP = hamiltonProduct(self, P)
            RPRt = hamiltonProduct(RP, Rt)
            Vec = Vector(RPRt.x, RPRt.y, RPRt.z)
            return Vec
        else:
            raise TypeError("Operand should be a Vector")

    def conjugate(self):
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __len__(self):
        return 4

class State():

    def __init__(self, mass=0.0, pos=Vector(), vel=Vector(), quat=Quaternion(), omega=Vector()):
        self.mass       = mass
        self.position   = pos
        self.velocity   = vel
        self.quaternion = quat
        self.bodyrate   = omega

    def __getitem__(self, item):
        if isinstance(item, int):
            if item >= 0 and item < len(self.__dict__):
                return list(self.__dict__.values())[item]
            else:
                raise IndexError(f"There are only {len(self.__dict__)} state variables")
        else:
            raise TypeError("Operand should be a positive int")
        
    def __setitem__(self, item, value):
        if isinstance(item, int):
            if item >= 0 and item < len(self.__dict__):
                key = list(self.__dict__.keys())[item]
                self.__dict__[key] = value
            else:
                raise IndexError(f"There are only {len(self.__dict__)} state variables")
        else:
            raise TypeError("Operand should be a positive int")

    def __add__(self, other):
        if isinstance(other, State):
            newstate = State()
            for i in range(0,len(self.__dict__),1):
                if isinstance(self[i], Quaternion):
                    qw = self[i].w + other[i].w 
                    qx = self[i].x + other[i].x
                    qy = self[i].y + other[i].y
                    qz = self[i].z + other[i].z
                    newstate[i] = Quaternion(qw, qx, qy, qz)
                else:
                    newstate[i] = self[i] + other[i]
            return newstate
        else:
            raise TypeError("Operand must be a State")
    
    def __sub__(self, other):
        if isinstance(other, State):
            newstate = State()
            for i in range(0,len(self.__dict__),1):
                if isinstance(self[i], Quaternion):
                    qw = self[i].w - other[i].w 
                    qx = self[i].x - other[i].x
                    qy = self[i].y - other[i].y
                    qz = self[i].z - other[i].z
                    newstate[i] = Quaternion(qw, qx, qy, qz)
                else:
                    newstate[i] = self[i] - other[i]
            return newstate
        else:
            raise TypeError("Operand must be a State")
    
    def __mul__(self, other):
        if isinstance(other, State):
            newstate = State()
            for i in range(0,len(self.__dict__),1):
                newstate[i] = self[i] * other[i]
            return newstate
        elif isinstance(other, (int, float)):
            newstate = State()
            for i in range(0,len(self.__dict__),1):
                newstate[i] = self[i] * other
            return newstate
        else:
            raise TypeError("Operand must be a State, int or float")
        
    def __rmul__(self, other):
        return self * other
        
    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            newstate = State()
            for i in range(0,len(self.__dict__),1):
                newstate[i] = self[i] / other
            return newstate
        else:
            raise TypeError("Operand must be int, or float")
        
    def __eq__(self, other):
        if isinstance(other, State):
            for i in range(0,len(self.__dict__),1):
                if self[i] != other[i]:
                    return False
            return True
        else:
            raise TypeError("Operand must be a State")
        
    def __str__(self):
        out = str(self[0])
        for i in range(1,len(self.__dict__),1):
            out = out + ", " + str(self[i])
        return f'State({out})'
    
    def __repr__(self):
        return self.__str__()

class Sensor():

    def __init__(self, name: str):
        self.name = name
        self.data = Vector(0,0,0)
        self.function = None
        self.power = False
    
    def setMethod(self, function, args=[]):
        self.function = function
        self.args = args

    def update(self):
        if self.power == True:
            self.data = self.function(self.attachedTo, self.args)
        else:
            self.data = self.data * 0

    def __repr__(self):
        return str(self.data)
    
class Controller():

    def __init__(self, name: str):
        self.name = name
        self.data = Vector(0,0,0)
        self.function = None
        self.power = False
    
    def setMethod(self, function, args=[]):
        self.function = function
        self.args = args

    def update(self):
        if self.power == True:
            self.data = self.function(self.attachedTo, self.args)
        else:
            self.data = self.data * 0

    def __repr__(self):
        return str(self.data)
    
class Actuator():

    def __init__(self, name: str):
        self.name = name
        self.data = Vector(0,0,0)
        self.function = None
        self.power = False
    
    def setMethod(self, function, args=[]):
        self.function = function
        self.args = args

    def update(self):
        if self.power == True:
            self.data = self.function(self.attachedTo, self.args)
        else:
            self.data = self.data * 0

    def __repr__(self):
        return str(self.data)
    
class Sked():

    def __init__(self, name: str, file=None):
        self.name    = name
        self.binary  = []
        self.text    = []
        self.read(file)
        
    def read(self, file=None):
        if file != None:
            self.binary = open(file, 'rb').readlines()
            self.text = open(file, 'r').readlines()
        else:
            raise TypeError("Input argument must a valid sked text file")
        
    def size(self):
        return len(self.text)

    def __repr__(self):
        return str(self.text)
    
    def __getitem__(self, item):
        if isinstance(item, int):
            return self.text[item]
        else:
            raise TypeError("Index value should be an integer")
        
class Spacecraft():

    def __init__(self, name):
        self.name  = name
        self.size  = Vector(0,0,0)
        self.state = State()
        
        self.netforce    = Vector(0,0,0)
        self.nettorque   = Vector(0,0,0)
        self.netmomentum = Vector(0,0,0)
        self.inertia     = Matrix(Vector(1,0,0),Vector(0,1,0),Vector(0,0,1))
        self.updateInertia = True

        self.location = Vector(0,0,0)
        self.system = None

        self.recorder = None
        self.sensors = {}
        self.controllers = {}
        self.actuators= {}
        
        self.torques = {}

        self.dipole = Vector(0.0, 0.0, 0.0)

        self.gravityTYPE     = "SPHERICAL2BODY"
        self.atmosphereTYPE  = "NONE"
        self.magnetfieldTYPE = "NONE"

        self.sked        = None
        self.nextCMD     = None
        self.nextCMDline = None
        self.idxCMD      = None
        self.unixTime    = 0
        self.continueCMD = True

    def loadSked(self, other: Sked):
        if isinstance(other, Sked):
            self.sked = other
            self.idxCMD = 0
            self.nextCMD = self.sked[self.idxCMD]
            self.nextCMDline = self.nextCMD.replace('\n','').replace(' ','').split(',')
            self.unixTime = int(calendar.timegm(self.system.datenow().utctimetuple()))
        else:
            raise TypeError("Input argument is not a valid class of type Sked")

    def updateUnixTime(self, cycle=1):
        if int(calendar.timegm(self.system.datenow().utctimetuple())) == self.unixTime + cycle:
            self.unixTime = int(calendar.timegm(self.system.datenow().utctimetuple()))
            if self.sked != None and self.continueCMD:
                self.processSked()
        self.updateComponents()
        
    def processSked(self):
        if int(self.nextCMDline[0]) == self.unixTime or int(self.nextCMDline[0]) < 0:
            print(' Execute CMD: '+str(self.nextCMDline))
            self.COMMANDEXEC(self.nextCMDline[1], self.nextCMDline[2])
            if self.idxCMD < self.sked.size()-1:
                self.idxCMD         = self.idxCMD + 1
                self.nextCMD        = self.sked[self.idxCMD]
                self.nextCMDline    = self.nextCMD.replace('\n','').replace(' ','').split(',')
                self.continueCMD    = True
            else:
                self.continueCMD = False

    def COMMANDEXEC(self, command: str, arg=[]):
        done = False
        if command == 'Components' and arg == 'ON':
            for sensor in self.sensors.values():
                sensor.power = True
            for controller in self.controllers.values():
                controller.power = True
            for actor in self.actuators.values():
                actor.power = True
            done = True

        if command == 'Components' and arg == 'OFF':
            for sensor in self.sensors.values():
                sensor.power = False
            for controller in self.controllers.values():
                controller.power = False
            for actor in self.actuators.values():
                actor.power = False
            done = True

        if command in self.sensors.keys() and (arg == 'ON' or arg == 'OFF'):
            if arg == 'ON':
                self.sensors[command].power = True; done = True
            if arg == 'OFF':
                self.sensors[command].power = False; done = True

        if command in self.controllers.keys() and (arg == 'ON' or arg == 'OFF'):
            if arg == 'ON':
                self.controllers[command].power = True; done = True
            if arg == 'OFF':
                self.controllers[command].power = False; done = True

        if command in self.actuators.keys() and (arg == 'ON' or arg == 'OFF'):
            if arg == 'ON':
                self.actuators[command].power = True; done = True
            if arg == 'OFF':
                self.actuators[command].power = False; done = True

        if not done:
            print('\t No matching CMD found for '+str(self.nextCMDline))
            print(command)

    def updateComponents(self):
        self.updateSensors()
        self.updateControllers()
        self.updateActuators()        

    def setAtmosphereModel(self, other):
        if isinstance(other, str):
            if (other == "NONE" or other == "US76" or other == "CIRA12"):
                self.atmosphereTYPE = other
            else:
                raise ValueError("Input str is not a valid AtmosphereModel")
        else:
            raise TypeError("Operang should be str")

    def getmass(self):
        return self.state.mass

    def setmass(self, other):
        if isinstance(other, (int, float)):
            self.state.mass = other
            self.inertia = rectbodyInertia(self.size, self.state.mass)
        else:
            raise TypeError("Operand should be int or float")

    def setinertia(self, other):
        if isinstance(other, Matrix):
            self.inertia = other
        else:
            raise TypeError("Operand should be a Matrix")
        
    def getinertia(self, other):
        return self.inertia

    def getsize(self):
        return self.size
    
    def setsize(self, other):
        if isinstance(other, Vector):
            self.size = other
        else:
            raise TypeError("Operand should be a Vector")

    def getposition(self):
        return self.state.position
    
    def setposition(self, other):
        if isinstance(other, Vector):
            self.state.position = other
        else:
            raise TypeError("Operand should be a Vector")
        
    def getvelocity(self):
        return self.state.velocity
    
    def setvelocity(self, other):
        if isinstance(other, Vector):
            self.state.velocity = other
        else:
            raise TypeError("Operand should be a Vector")

    def getorientation(self, unit='deg'):
        if unit == 'deg':
            return self.state.quaternion.YPR_toRPY_vector()*R2D
        elif unit == 'rad':
            return self.state.quaternion.YPR_toRPY_vector()
        else:
            raise ValueError("Ooperance should be 'deg' or 'rad'")

    def setorientation(self, other):
        if isinstance(other, Vector):
            self.state.quaternion = other.RPY_toYPR_quaternion()
        else:
            raise TypeError("Operand should be a vector in 'deg'")

    def getbodyrate(self):
        return self.state.bodyrate * R2D

    def setbodyrate(self, other):
        if isinstance(other, Vector):
            self.state.bodyrate = other * D2R
        else:
            raise TypeError("Operand should be a vector in 'deg/s'")

    def derivative(self, state: State, time):
        self.clearKinetics()
        deltaState = State()

        deltaState.mass = 0

        deltaState.position = state.velocity

        self.netforce = self.netforce \
                      + systemGravity(self.system, state.mass, state.position, self.gravityTYPE) \
                      + systemAtmosphere(self.system, state, self.size, self.atmosphereTYPE)
        
        deltaState.velocity = self.netforce/state.mass

        if self.updateInertia:
            self.inertia = rectbodyInertia(self.size, state.mass)   
            
        if self.system.orbitPropOnly == False:
            deltaState.quaternion = quaternionDerivative(state.bodyrate, state.quaternion)

            self.netmomentum = self.netmomentum + self.inertia*state.bodyrate
            self.nettorque = self.nettorque \
                           + self.calculateTorques() \
                           + systemMagneticField(self.system, state, time, self.dipole, self.magnetfieldTYPE)

            deltaState.bodyrate = self.inertia.inverse()*(self.nettorque-state.bodyrate.cross(self.netmomentum))

        return deltaState
    
    def clearKinetics(self):
        self.netforce    = Vector(0,0,0)
        self.nettorque   = Vector(0,0,0)
        self.netmomentum = Vector(0,0,0)

    def addSensor(self, other):
        if isinstance(other, Sensor):
            self.sensors[other.name] = other
            other.attachedTo = self
            other.system = self.system
            self.recorder.addItem(other)

    def getSensors(self):
        return self.sensors
    
    def updateSensors(self):
        for sensor in self.sensors.values():
            sensor.update()

    def addController(self, other):
        if isinstance(other, Controller):
            self.controllers[other.name] = other
            other.attachedTo = self
            other.system = self.system
            self.recorder.addItem(other)

    def getControllers(self):
        return self.controllers
    
    def updateControllers(self):
        for control in self.controllers.values():
            control.update()

    def addActuator(self, other):
        if isinstance(other, Actuator):
            self.actuators[other.name] = other
            other.attachedTo = self
            other.system = self.system
            self.recorder.addItem(other)
            self.addTorque(other)

    def getActuators(self):
        return self.actuators
    
    def updateActuators(self):
        for actor in self.actuators.values():
            actor.update()

    def addTorque(self, other):
        self.torques[other.name] = other

    def calculateTorques(self):
        total_torque = Vector(0,0,0)
        for torque in self.torques.values():
            total_torque = total_torque + torque.data
        return total_torque
    
    def getTorques(self):
        return self.torques

    def __getitem__(self, item):
        if isinstance(item, str):
            if item == "State": 
                return self.state
            elif item == "Netforce": 
                return self.netforce
            elif item == "Nettorque": 
                return self.nettorque
            elif item == "Netmoment": 
                return self.netmomentum
            elif item == "Location": 
                return self.location
            elif item == "Sunlocation":
                return self.system.sunLocation
            elif item == "Sunvector":
                return self.system.sunVector
            elif item == "SpecificAngularMomentum": 
                sam = self.state.position.cross(self.state.velocity).magnitude()
                return sam
            elif item == "SpecificMechanicalEnergy":
                pos = self.state.position
                vel = self.state.velocity
                sme = (vel.magnitude()**2/2 - (self.system.mu/pos.magnitude()))
                return sme
            elif item == "BodyAngularMomentum":
                bam = self.netmomentum.magnitude()
                return bam
            elif item in list(self.sensors.keys()):
                return self.getSensors()[item].data
            
            elif item in list(self.controllers.keys()):
                return self.getControllers()[item].data
            
            elif item in list(self.actuators.keys()):
                return self.getActuators()[item].data
            
            elif item in list(self.torques.keys()):
                return self.getTorques()[item].data
            else:
                raise TypeError("Operand should be a recorder item")
        else:
            raise TypeError("Operand should be a recorder item in str")

class GroundStation():

    def __init__(self, name, latitude, longitude, altitude):
        self.name = name
        self.longitude = longitude  ## deg
        self.latitude = latitude    ## deg
        self.altitude = altitude    ## meters

        self.min_elevation = 0

    def setElevation(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.min_elevation = other

class Pass():
    def __init__(self, aos: datetime.datetime, tca: datetime.datetime, elev, los: datetime.datetime):
        self.AOS = aos
        self.TCA = tca
        self.LOS = los
        self.angleTCA = elev

        self.duration = (los-aos).total_seconds()
    
    def __str__(self):
        return f'Pass(AOS:{self.AOS}, TCA:{self.TCA}, MaxElev:{self.angleTCA}, LOS:{self.LOS}, Duration:{self.duration})'
    
    def __repr__(self):
        return self.__str__()

class Recorder():

    def __init__(self, datetime: datetime.datetime,  spacecraft: Spacecraft, datalist: list):
        self.attachedTo   = spacecraft
        self.attachedWhen = datetime
        self.dataDict = { "Datetime" : [] }

        for item in datalist:
            self.dataDict[item] = []
    
    def addItem(self, item):
        self.dataDict[item.name] = []

    def update(self, datetime: datetime.datetime):
        Datetime = datetime
        self.dataDict["Datetime"].append(Datetime)

        for item in list(self.dataDict.keys())[1:]:
            self.dataDict[item].append(self.attachedTo[item])

    def __getitem__(self, item):
        if isinstance(item, str) and item in self.dataDict.keys():
            return self.dataDict[item]
        else:
            raise TypeError("Operand should be recorder item")

class LEOSS():

    def __init__(self):
        self.spacecraftObjects = []
        self.recorderObjects = {}

        self.time = 0.0
        self.mu = 398600.4418e9
        self.radi = 6378.137e3

        self.epochDT(datetime.datetime.today())
        self.sunVector, self.sunLocation = systemSun(self)

        self.orbitPropOnly = False

    def epochDT(self, dt: datetime.datetime):
            self.epoch(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond)

    def epoch(self, year=0, month=0, day=0, hour=0, minute=0, second=0, microsecond=0):
            
            self.datetime0 = datetime.datetime(year, month, day, hour, minute, second, microsecond)
            self.jdate0 = 367*year - int((7*(year + int((month+9)/12)))/4) + int(275*month/9) + day + 1721013.5
            
            hours  = hour + minute/60 + second/3600 + microsecond/3600000000
            j2000  = 2451545
            T0     = (self.jdate0 - j2000)/36525
            
            gmst0_ =  100.4606184 + 36000.77004*T0 + 0.000387933*(T0**2) - (2.583e-8)*(T0**3)

            self.gmst0 = gmst0_%360
            self.gmst  = self.gmst0 + 360.98564724*hours/24

    def datenow(self):
        return self.datetime0 + datetime.timedelta(seconds=self.time)

    def addSpacecraft(self, name, recordList: list = []):
        
        recordList = ['State','Location','Netforce','Nettorque','Netmoment','Sunlocation', \
                'SpecificAngularMomentum','SpecificMechanicalEnergy','BodyAngularMomentum'] \
                + recordList
        spacecraft = Spacecraft(name)
        spacecraft.system = self
        self.spacecraftObjects.append(spacecraft)
        recorder = Recorder(self.datenow(), spacecraft, recordList)
        self.recorderObjects[name] = recorder
        spacecraft.recorder = recorder

    def listSpacecraft(self):
        names = []
        for spacecraft in self.spacecraftObjects:
            names.append(spacecraft.name)
        return names
    
    def getSpacecrafts(self):
        spacecraftDict = {}
        for spacecraft in self.spacecraftObjects:
            spacecraftDict[spacecraft.name] = spacecraft
        return spacecraftDict
    
    def getRecorders(self):
        return self.recorderObjects
    
    def numSpacecraft(self):
        return len(self.spacecraftObjects)
    
    def advance1timestep(self, deltaTime):

        self.sunVector, self.sunLocation = systemSun(self)

        for spacecraft in self.spacecraftObjects:

            spacecraft.location = self.locate(spacecraft, self.time)
            spacecraft.updateUnixTime()
            # spacecraft.updateSensors()
            # spacecraft.updateControllers()
            # spacecraft.updateActuators()
            newstate = runggeKutta4(spacecraft.derivative, spacecraft.state, self.time, deltaTime)
            newstate.quaternion = newstate.quaternion.normalize()

            self.recorderObjects[spacecraft.name].update(self.datenow()) #+datetime.timedelta(seconds=deltaTime)

            spacecraft.state = newstate

        self.time = self.time + deltaTime

    def updateRecorders(self):
        for spacecraft in self.spacecraftObjects:
            self.recorderObjects[spacecraft.name].update(self.datenow())
    
    def __getitem__(self, item):
        if isinstance(item, int):
            if item >= 0 and item < self.numSpacecraft():
                return self.spacecraftObjects[item]
            else:
                raise IndexError(f"There are only {self.numSpacecraft()} spacecraft objects")
        else:
            raise TypeError("Operand should be a positive int")
        
    def locate(self, spacecraft: Spacecraft, time):
        
        position = spacecraft.getposition()

        mag = position.magnitude()

        theta = math.acos(position.z/mag)
        psi   = math.atan2(position.y,position.x)

        latitude  = 90 - (theta*R2D)
        longitude = psi*R2D
        altitude  = (mag-self.radi)/1000

        xy = math.sqrt(position.x**2+position.y**2)

        gd_theta = latitude*D2R
        C = 0
        gd = 0
        e2 = 0.006694385000

        while True:
            C = self.radi/math.sqrt(1-e2*math.sin(gd_theta)*math.sin(gd_theta))
            gd = math.atan2(position.z+C*e2*math.sin(gd_theta),xy)
            if abs(gd-gd_theta) < 1e-6:
                gd_theta = gd
                break
            gd_theta = gd
        
        h_ellp = ( xy/math.cos(gd_theta) ) - C  
        
        altitude = h_ellp/1e3
        latitude = gd_theta*R2D

        gmst_ = self.gmst + time*(360.98564724)/(24*3600) 
        longitude = longitude - gmst_
        if longitude < 0:
            longitude = (((longitude/360) - int(longitude/360)) * 360) + 360    
        if longitude > 180:
            longitude = -360 + longitude
        
        location = Vector(latitude, longitude, altitude)
        return location


def systemGravity(system: LEOSS, mass, position, gravityTYPE = ""):
    '''
    ------------------------------------------------------------------------------------------
    Computes the gravitation force and gravitational perturbation forces on the spacecraft due 
    to Earth's oblateness.
    (only harmonics until J4).
    ------------------------------------------------------------------------------------------
    Algorithm is derived from [1], also see [2].
    J values are taken from [1]
    ------------------------------------------------------------------------------------------
    References:
        [1] Fundamentals of Astrodynamics and Applications by David Vallado (2013) pp.594
        [2] Analytical Mechanics of Space Systems by Hanspeter Schaub (2009) pp.553
    ------------------------------------------------------------------------------------------
    '''
    if gravityTYPE == "NONE" or "":
        return Vector(0.0, 0.0, 0.0)
    
    if gravityTYPE == "SPHERICAL2BODY":
        rho = position.magnitude()
        return -(system.mu*mass/(rho**3))*position
    
    if gravityTYPE == "EARTHJ2":
        rho = position.magnitude()
        force_2body = -(system.mu*mass/(rho**3))*position

        J2 = 1082.6276e-6
        magnitude2 = (3/2)*(J2*system.mu*(system.radi**2))/(rho**4) 
        k = 5*(position.z**2)/(rho**2)
        vector = Vector( (position.x/rho)*(k-1), (position.y/rho)*(k-1), (position.z/rho)*(k-1)  )

        force_total = force_2body + mass*magnitude2*vector
        return force_total
    
    if gravityTYPE == "EARTHJ3":
        rho = position.magnitude()
        force_2body = -(system.mu*mass/(rho**3))*position

        J2 = 1082.6276e-6
        magnitude2 = (3/2)*(J2*system.mu*(system.radi**2))/(rho**4) 
        k2 = 5*(position.z**2)/(rho**2)
        vector2 = Vector( (position.x/rho)*(k2-1), (position.y/rho)*(k2-1), (position.z/rho)*(k2-1)  )

        forceJ2 = mass*magnitude2*vector2
    
        J3 = -2.5327e-6
        magnitude3 = (5/2)*(J3*system.mu*(system.radi**3))/(rho**6)
        k3 = 7*(position.z**3)/(rho**2)
        vector3 = Vector( (position.x/rho)*(k3-3*position.z), \
                          (position.y/rho)*(k3-3*position.z),   \
                          (1/rho)*(k3*position.z + (3/5)*(rho**2) - 6*position.z*position.z) )
        
        forceJ3 = mass*magnitude3*vector3
        
        force = force_2body + forceJ2 + forceJ3

        return force
    
    if gravityTYPE == "EARTHJ4":
        rho = position.magnitude()
        force_2body = -(system.mu*mass/(rho**3))*position

        J2 = 1082.6276e-6
        magnitude2 = (3/2)*(J2*system.mu*(system.radi**2))/(rho**4) 
        k2 = 5*(position.z**2)/(rho**2)
        vector2 = Vector( (position.x/rho)*(k2-1), (position.y/rho)*(k2-1), (position.z/rho)*(k2-1)  )

        forceJ2 = mass*magnitude2*vector2
    
        J3 = -2.5327e-6
        magnitude3 = (5/2)*(J3*system.mu*(system.radi**3))/(rho**6)
        k3 = 7*(position.z**3)/(rho**2)
        vector3 = Vector( (position.x/rho)*(k3-3*position.z), \
                          (position.y/rho)*(k3-3*position.z),   \
                          (1/rho)*(k3*position.z + (3/5)*(rho**2) - 6*position.z*position.z) )
        
        forceJ3 = mass*magnitude3*vector3
        
        J4 = -0.1619e-6
        magnitude4 = (15/8)*(J4*system.mu*(system.radi**4))/(rho**6) 
        k4 = 21*(position.z**4)/(rho**4)
        l4 = 14*(position.z**2)/(rho**2)
        vector4 = Vector( (position.x/rho)*( 1 - l4 + k4), \
                          (position.y/rho)*( 1 - l4 + k4),   \
                          (position.z/rho)*( 5 - (5/3)*l4 + k4) )
        
        forceJ4 = mass*magnitude4*vector4

        force = force_2body + forceJ2 + forceJ3 + forceJ4

        return force

def systemMagneticField(system: LEOSS, state, time, dipole, fieldTYPE = ""):
    
    if fieldTYPE == "NONE" or "":
        return Vector(0.0, 0.0, 0.0)
    
    if fieldTYPE == "EARTH":
        position = state.position
        mag = position.magnitude()

        theta = math.acos(position.z/mag)
        psi   = math.atan2(position.y,position.x)

        latitude  = 90 - (theta*R2D)
        longitude = psi*R2D
        altitude  = (mag-system.radi)/1000

        xy = math.sqrt(position.x**2+position.y**2)

        gd_theta = latitude*D2R
        C = 0
        gd = 0
        e2 = 0.006694385000

        while True:
            C = system.radi/math.sqrt(1-e2*math.sin(gd_theta)*math.sin(gd_theta))
            gd = math.atan2(position.z+C*e2*math.sin(gd_theta),xy)
            if abs(gd-gd_theta) < 1e-6:
                gd_theta = gd
                break
            gd_theta = gd
        
        h_ellp = ( xy/math.cos(gd_theta) ) - C  
        
        altitude = h_ellp/1e3
        latitude = gd_theta*R2D

        gmst_ = system.gmst + time*(360.98564724)/(24*3600) 
        longitude = longitude - gmst_
        if longitude < 0:
            longitude = (((longitude/360) - int(longitude/360)) * 360) + 360    
        if longitude > 180:
            longitude = -360 + longitude
            
        location = Vector(latitude, longitude, altitude)
        magfield = IGRF.igrf_value(location[0], location[1], location[2], system.datenow().year)[3:6]
        magfield_NED_vector = Vector(magfield[0], magfield[1], magfield[2]) * 1e-9

        R = position.magnitude()
        theta = math.acos(position.z/R)
        psi   = math.atan2(position.y, position.x)
        RPY = Vector(0, (theta+math.pi)*R2D, psi*R2D)

        magfield_inertial_vector = RPY.RPY_toYPR_quaternion().toMatrix().transpose()*magfield_NED_vector

        quaternion = state.quaternion
        magfield_body_vector = quaternion.toMatrix()*magfield_inertial_vector

        disturbance_torque = dipole.cross(magfield_body_vector)

        return disturbance_torque

def systemAtmosphere(system: LEOSS, state, dimension, atmosphereTYPE = ""):

    if atmosphereTYPE == "NONE" or "":
        return Vector(0.0, 0.0, 0.0)
    
    if atmosphereTYPE == "CIRA12":
        '''
        -------------------------------------------------------------------------------------------------
        Computes the atmospheric drag force on the spacecraft in moderate solar and geomagnetic activity.
        This follows the (latest) CIRA-2012 Earth's Atmosphere Model
            This is based from JB2008 model (Jacchia-Bowman) based on Jacchia model heritage
            (Note that CIRA-2012 has four semi-empirical models, JB2008 is the one recommended 
            for use in determining drag in LEO above 120 km)
        Applicable only from 180 to 900 km
        -------------------------------------------------------------------------------------------------
        The atmospheric model is polyfitted (order=4) based from [2] using [1]
        Algorithm for drag force is based from [4]
        The drag coefficeint is assumed to be the standard 2.2 as in [3]
        The reference area of the spacecraft A is the mean surface area as in [3]
        -------------------------------------------------------------------------------------------------
        References: 
            [1] COSPAR Internation Reference Atmosphere Model (CIRA-2012) pp.20-25
            [2] Bare Electrodynamic Tether Mission Analysis (BETsMA) ResearchGate (2014) pp.14
            [3] https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1144&context=smallsat
            [4] Orbital Mechanics for Engineering Students by Howard Curtis (2014) pp.658
        -------------------------------------------------------------------------------------------------
        '''
        # moderate solar and geomagnetic activities - JB2008
        # F10.7 avg = 140 solar proxy 
        # S10.7 avg = 125 solar index
        # M10.7 avg = 125 solar proxy 
        # Y10.7 avg = 125 solar index
        # Ap        = 15  daily planetary geomagnetic index
        # Dst       = -15 hourly disturbance storm time ring geomagnetic index
        # x = np.arange(100,920,20)
        # y = [ 5.47e-07, 2.40e-08, 3.98e-09, 1.36e-09, 6.15e-10, 3.17e-10, 1.77e-10, 1.05e-10, 6.47e-11, 4.12e-11,
        #        2.69e-11, 1.80e-11, 1.23e-11, 8.48e-12, 5.95e-12, 4.22e-12, 3.02e-12, 2.18e-12, 1.59e-12, 1.17e-12,
        #        8.60e-13, 6.39e-13, 4.77e-13, 3.58e-13, 2.71e-13, 2.06e-13, 1.57e-13, 1.20e-13, 9.28e-14, 7.19e-14,
        #        5.60e-14, 4.40e-14, 3.48e-14, 2.79e-14, 2.26e-14, 1.85e-14, 1.53e-14, 1.28e-14, 1.08e-14, 9.27e-15,
        #        8.01e-15 ]
        
        # z = np.polyfit(x[4:],np.log10(y[4:]),15)
        # p = np.poly1d(z)
        # xp = np.arange(180,900,1)
        # plt.plot(x[4:],y[4:],'r-')
        # plt.plot(xp,10**p(xp),'g.-')
        # plt.plot(x[4:],np.log10(y[4:]),'r-')
        # plt.plot(xp,p(xp),'g.-')
        # plt.plot(x[4:],10**p(x[4:])-y[4:],'r-')
        # plt.show()
        
        # JB2008 (moderate)
        pn = [ 1.99771025e-11, -4.73018227e-08, 4.41628966e-05, -2.50878092e-02, -5.89884573e+00]
        
        def f(input):
            return  pn[0]*input**(4) \
                    +  pn[1]*input**(3) \
                    +  pn[2]*input**(2) \
                    +  pn[3]*input**(1) \
                    +  pn[4]  
        
        pos = state.position
        rho = pos.magnitude() - system.radi
        z   = rho/1000
        
        if z >= 900:
            z = 900
        elif z <= 180:
            z = 180
        
        p = 10**f(z)
        
        D = 2.2
        dim = dimension
        A = ( dim.x*dim.y + dim.x*dim.z + dim.y*dim.z ) / 3
        # w_earth = 360.98564724*D2R/(24*60*60) * np.array([0.0, 0.0, 1.0])
        w = Vector(0.0, 0.0, 7.29211585e-05)

        v_sc  = state.velocity
        v_atm = w.cross(pos)
        v_rel = v_sc - v_atm
        
        vr    = math.sqrt(v_rel.x**2+v_rel.y**2+v_rel.z**2)
        unit_vr = v_rel/vr
        
        drag = (-0.5*p*D*A*vr*vr)*unit_vr

        return drag

    if atmosphereTYPE == "US76":
        '''
        -----------------------------------------------------------------------------------------
        Computes the atmospheric drag force on the spacecraft.
        This follows the Exponential Atmospheric Model which uses the..
            U.S. Standard Atmosphere 1976 (USSA76) for 0 km
            COSPAR International Reference Atmosphere 1972 (CIRA72) for 25-500 km
            CIRA72 with exospheric temperature T = 1000K for 500-1000 km
        Applicable only from altitude of 0 to 1000 km. 
        -----------------------------------------------------------------------------------------
        Algorithm for atmosphere density is based from [1]
        Algorithm for drag force is based from [3]
        The drag coefficeint is assumed to be the standard 2.2 as in [2]
        The reference area of the spacecraft A is the mean surface area as in [2]
        -----------------------------------------------------------------------------------------
        References: 
            [1] Fundamentals of Astrodynamics and Applications by David Vallado (2013) pp.567
            [2] https://digitalcommons.usu.edu/cgi/viewcontent.cgi?article=1144&context=smallsat
            [3] Orbital Mechanics for Engineering Students by Howard Curtis (2014) pp.658
        -----------------------------------------------------------------------------------------
        '''
        pos = state.position
        rho = pos.magnitude() - system.radi
        z   = rho/1000

        h = [  0,  25,  30,  40,  50,  60,  70, 
            80,  90, 100, 110, 120, 130, 140,
            150, 180, 200, 250, 300, 350, 400,
            450, 500, 600, 700, 800, 900, 1000 ]
        
        p0 = [     1.225,  3.899e-2,  1.774e-2,  3.972e-3,  1.057e-3,  3.206e-4,  8.770e-5,
                1.905e-5,  3.396e-6,  5.297e-7,  9.661e-8,  2.438e-8,  8.484e-9, 3.8345e-9,
                2.070e-9, 5.464e-10, 2.789e-10, 7.248e-11, 2.418e-11, 9.518e-12, 3.725e-12,
            1.585e-12, 6.967e-13, 1.454e-13, 3.614e-14, 1.170e-14, 5.245e-15, 3.019e-15 ]
        
        H = [  7.249,  6.349,  6.682,   7.554,   8.382,   7.714,  6.549, 
            5.799,  5.382,  5.877,   7.263,   9.473,  12.636, 16.149,
            22.523, 29.740, 37.105,  45.546,  53.628,  53.298, 58.515,
            60.828, 63.822, 71.835,  88.667, 124.640, 181.050, 268.00 ]
        
        if z > 1000:
            z = 1000
        elif z < 0:
            z = 0
        
        i = 0
        ### interpolation interval
        jlist = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                21, 22, 23, 24, 25, 26, 27 ]
        for j in jlist:
            if z >= h[j] and z < h[j+1]:
                i = j
                break
            
        if z == 1000:
            i = 27
            
        ### exponential interpolation
        p = p0[i]*math.exp(-(z-h[i])/H[i])
        
        D = 2.2
        dim = dimension
        A = ( dim.x*dim.y + dim.x*dim.z + dim.y*dim.z ) / 3
        # w_earth = 360.98564724*D2R/(24*60*60) * np.array([0.0, 0.0, 1.0])
        w = Vector(0.0, 0.0, 7.29211585e-05)

        v_sc  = state.velocity
        v_atm = w.cross(pos)
        v_rel = v_sc - v_atm
        
        vr    = math.sqrt(v_rel.x**2+v_rel.y**2+v_rel.z**2)
        unit_vr = v_rel/vr
        
        drag = (-0.5*p*D*A*vr*vr)*unit_vr

        return drag

def systemSun(system: LEOSS):
    # AU = 149597870.691
    
    date = system.datenow()
    second = date.second
    minute = date.minute
    hour   = date.hour
    day    = date.day
    month  = date.month
    year   = date.year

    C = ((((second/60) + minute)/60) + hour)/24
    jdate = 367*year - int((7*(year + int(month+9)/12))/4) + int(275*month/9) + day + 1721013.5 + C
    
    n  = jdate - 2451545
    # cy = n/36525
    M  = 57.528 + 0.9856003*n
    M  = M % 360
    L  = 280.460 + 0.98564736*n
    L  = L % 360
    Lamda = L + 1.915*math.sin(M*D2R) + 0.020*math.sin(2*M*D2R)
    Lamda = Lamda % 360
    eps   = 23.439 - 0.0000004*n
    u   = Vector( math.cos(Lamda*D2R) , math.sin(Lamda*D2R)*math.cos(eps*D2R), math.sin(Lamda*D2R)*math.sin(eps*D2R) )
    # rS  = (1.00014 - 0.01671*math.cos(M*D2R) - 0.000140*math.cos(2*M*D2R))*AU
    # r_S = rS * u

    sun_unitVector = u

    mag = sun_unitVector.magnitude()

    theta = math.acos(sun_unitVector.z/mag)
    psi   = math.atan2(sun_unitVector.y, sun_unitVector.x)

    latitude  = 90 - (theta*R2D)
    longitude = psi*R2D

    gmst_ = system.gmst + system.time*(360.98564724)/(24*3600) 
    longitude = longitude - gmst_
    if longitude < 0:
        longitude = (((longitude/360) - int(longitude/360)) * 360) + 360    
    if longitude > 180:
        longitude = -360 + longitude

    sun_LatLon = Vector( latitude, longitude, 0)

    return sun_unitVector, sun_LatLon

def runggeKutta4(derivative, state, time, deltaTime):
    k1 = derivative(state, time)
    k2 = derivative(state + k1*deltaTime/2, time + deltaTime/2)
    k3 = derivative(state + k2*deltaTime/2, time + deltaTime/2)
    k4 = derivative(state + k3*deltaTime, time + deltaTime)
    k  = (1/6)*(k1 + 2*k2 + 2*k3 + k4)*deltaTime
    return state + k

def simulate(system: LEOSS, timeEnd, timeStep=1/32, orbitPropOnly = False):

    system.orbitPropOnly = orbitPropOnly

    while system.time <= timeEnd:
        system.advance1timestep(timeStep)
    system.time = system.time - timeStep

def simulateProgress(system: LEOSS, timeEnd, timeStep=1/32, orbitPropOnly = False):

    system.orbitPropOnly = orbitPropOnly

    print("\nRun Simulation (from "+str(system.time)+" to "+str(timeEnd)+", step="+str(timeStep)+")")
    t0 = clock.time()

    pbar = tqdm(total=timeEnd-system.time+timeStep, position=0, desc='Simulating', bar_format='{l_bar}{bar:25}{r_bar}{bar:-25b}')
    
    while(system.time <= timeEnd):
        prev_time = system.time
        system.advance1timestep(timeStep)        
        pbar.update(system.time - prev_time)
    system.time = system.time - timeStep
    pbar.close()

    t1 = clock.time()
    print("\nElapsed Time:\t"+str(t1-t0)+" sec.")

def PRVtoQuaternion(PRV: Vector, Angle, unit='deg'):
    if unit == 'deg':
        Angle = Angle*D2R
        unit = 'rad'
    if unit == 'rad':   
        vec = PRV.normalize()
        return Quaternion( math.cos(Angle/2), vec.x*math.sin(Angle/2), vec.y*math.sin(Angle/2), vec.z*math.sin(Angle/2) )
    else:
        raise ValueError("Unit should be either in 'deg' or 'rad'")
    
def quaternionDerivative(omega: Vector, quat: Quaternion):
    qdotW =       0*quat.w - omega.x*quat.x - omega.y*quat.y - omega.z*quat.z
    qdotX = omega.x*quat.w +       0*quat.x + omega.z*quat.y - omega.y*quat.z
    qdotY = omega.y*quat.w - omega.z*quat.x +       0*quat.y + omega.x*quat.z
    qdotZ = omega.z*quat.w + omega.y*quat.x - omega.x*quat.y +       0*quat.z
    return Quaternion( qdotW/2, qdotX/2, qdotY/2, qdotZ/2 )

def rectbodyInertia(size: Vector, mass):
    Lx = size.x
    Ly = size.y
    Lz = size.z
    x = Vector(Ly**2+Lz**2, 0, 0)
    y = Vector(0, Lx**2+Lz**2, 0)
    z = Vector(0, 0, Lx**2+Ly**2)
    return (mass/12.0) * Matrix(x,y,z)

def hamiltonProduct(q1: Quaternion, q2: Quaternion):

    W = q1.w*q2.w - q1.x*q2.x - q1.y*q2.y - q1.z*q2.z
    X = q1.w*q2.x + q1.x*q2.w + q1.y*q2.z - q1.z*q2.y
    Y = q1.w*q2.y - q1.x*q2.z + q1.y*q2.w + q1.z*q2.x
    Z = q1.w*q2.z + q1.x*q2.y - q1.y*q2.x + q1.z*q2.w

    return Quaternion(W, X, Y, Z)

def calculateJDate(sys: LEOSS):
    year  = sys.datenow().year
    month = sys.datenow().month
    day   = sys.datenow().day
    hour  = sys.datenow().hour
    minute = sys.datenow().minute
    second = sys.datenow().second
    print(year)
    print(month)
    print(day)
    print(hour)
    print(minute)
    print(second)
    C = ((((second/60) + minute)/60) + hour)/24
    JDate = 367*year - int((7*(year + int((month+9)/12)))/4) + int(275*month/9) + day + 1721013.5 + C
            
    return JDate

#### FUNCTIONS

def IDEAL_magnetometer_function(spacecraft: Spacecraft, args):
    location = spacecraft.location
    magfield = IGRF.igrf_value(location[0], location[1], location[2], spacecraft.system.datenow().year)[3:6]
    magfield_NED_vector = Vector(magfield[0], magfield[1], magfield[2]) * 1e-9

    position = spacecraft.state.position
    R = position.magnitude()
    theta = math.acos(position.z/R)
    psi   = math.atan2(position.y, position.x)
    RPY = Vector(0, (theta+math.pi)*R2D, psi*R2D)

    magfield_inertial_vector = RPY.RPY_toYPR_quaternion().toMatrix().transpose()*magfield_NED_vector

    quaternion = spacecraft.state.quaternion
    magfield_body_vector = quaternion.toMatrix()*magfield_inertial_vector

    return magfield_body_vector

def REAL_magnetometer_FUNC(spacecraft, args):
    '''
    !! TO ADD NOISE and RANDOMNESS !!
    Similar with the ideal magnetometer function with added delay options using args
    delay = args[0] = INT only and non-negative, the number of simulate time steps of sensor output delay
    
    recorder length should have enough data to capture delayed information
    - 1) takes the delayed recorder->location to measure the magnetic field (NED frame)
    - 2) takes the delayed spacecraft->position to get transformation from NED to inertial frame
    - 3) takes the transformation matrix from 3 to get the magnetic field (inertial frame)
    - 4) takes the delayed spacecraft->quaternion to get transformation from inertial to BODY frame
    - 5) takes the transformation matrix from 4 to get the magnetic field (BODY frame)
    '''
    if len(spacecraft.recorder['Location']) > args[0] and args[0] > -1:
        location = spacecraft.recorder['Location'][-args[0]-1]
        magfield = IGRF.igrf_value(location[0], location[1], location[2], spacecraft.recorder['Datetime'][-args[0]-1].year)[3:6]
        magfield_NED_vector = Vector(magfield[0], magfield[1], magfield[2]) * 1e-9

        position = spacecraft.recorder['State'][-args[0]-1].position
        R = position.magnitude()
        theta = math.acos(position.z/R)
        psi   = math.atan2(position.y, position.x)
        RPY = Vector(0, (theta+math.pi)*R2D, psi*R2D)

        magfield_inertial_vector = RPY.RPY_toYPR_quaternion().toMatrix().transpose()*magfield_NED_vector

        quaternion = spacecraft.recorder['State'][-args[0]-1].quaternion
        magfield_body_vector = quaternion.toMatrix()*magfield_inertial_vector
    else:
        magfield_body_vector = Vector(0,0,0)

    return magfield_body_vector

def IDEAL_bdotcontroller_function(spacecraft: Spacecraft, args):
    magfield_body_vector0 = Vector(0,0,0)
    time0 = spacecraft.system.datetime0

    control_moment = Vector(0,0,0)

    if len(spacecraft.recorder['ideal_MTM']) > 2:
        magfield_body_vector0 = spacecraft.recorder['ideal_MTM'][-1]
        time0 = spacecraft.recorder['Datetime'][-1]

    if len(spacecraft.recorder['ideal_MTM']) > 1:
        magfield_body_vector = spacecraft['ideal_MTM']
        time = spacecraft.system.datenow()
        
        delta_magfield_body_vector = magfield_body_vector - magfield_body_vector0
        delta_time = (time - time0).total_seconds()

        control_moment = -args[0] * (delta_magfield_body_vector/delta_time)

    return control_moment

def REAL_bdotcontroller_FUNC(spacecraft: Spacecraft, args):
    '''
    !! TO ADD NOISE and RANDOMNESS !!
    Similar with the ideal magnetometer function
    args[0] = INT or FLOAT, the controller gain
    args[1] = STR only, the name of the sensor object that the controller takes the input from

    control moment is zero unless the length of recorders is more than 1
    - 1) take the latest recorder->MTM sensor magnetic field (BODY frame) values
    - 2) take the latest recorder->datetime values
    - 3) take the current state spacecraftr->MTM sensor magnetic field (BODY frame) values
    - 4) take the current state spacecratft->datetime values
    - 5) calculate difference in magnetic field (BODY frame) between current and latest
    - 6) calcualte difference in datetime in seconds between current and latest
    - 7) take the ratio of 5/6 (this is the derivative of magnetic field)
    - 8) multiply the ratio with negative of controller gain
    '''
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

def ideal_magnetorquer_function(spacecraft: Spacecraft, args):
    
    control_moment = spacecraft['ideal_BDOT']
    magfield_body_vector = spacecraft['ideal_MTM']
    control_torque = control_moment.cross(magfield_body_vector)

    return control_torque

def REAL_magnetorquer_FUNC(spacecraft: Spacecraft, args):
    '''
    !! TO ADD NODES AND RANDOMNESS !!
    Similar with the ideal magnetorquer function
    args[0] - STR only, the name of the controller object that the actuator receives commands from

    - 1) takes the controller command output from args[0]
    - 2) takes the TRUE magnetic field (BODY frame) from ideal MTM
    - 3) calculate the magnetic torque generated by cross multiply 1 and 3
    '''

    control_moment = spacecraft[args[0]]
    magfield_body_vector = spacecraft['ideal_MTM']
    control_torque = control_moment.cross(magfield_body_vector)

    return control_torque

def REAL_gyroscope_FUNC(spacecraft, args):
    '''
    !! TO ADD NOISE and RANDOMNESS !!
    args[0] - INT only and non-negative, the number of simulate time steps of sensor output delay
    
    - 1) takes the delayed recorder->state->bodyrate values
    '''
    gyro_bodyrate = Vector(0,0,0)
    if len(spacecraft.recorder['State']) > args[0] and args[0] > -1:
        gyro_bodyrate = spacecraft.recorder['State'][-args[0]-1].bodyrate
    return gyro_bodyrate

def REAL_gps_FUNC(spacecraft, args):
    '''
    !! TO ADD NOISE and RANDOMNESS !!
    args[0] - INT only and non-negative, the number of simulate time steps of sensor output delay
    
    - 1) takes the delayed recorder->location values
    '''
    gps_position = Vector(0,0,0)
    if len(spacecraft.recorder['Location']) > args[0] and args[0] > -1:
        gps_position = spacecraft.recorder['Location'][-args[0]-1]
    return gps_position

def ideal_sunsensor_function(spacecraft: Spacecraft, args):
    
    quaternion = spacecraft.state.quaternion
    sun_body_vector = quaternion.toMatrix() * spacecraft['Sunvector']

    return sun_body_vector

def LVLHqerror_function(spacecraft: Spacecraft, args):
    r = spacecraft.state.position.normalize()
    v = spacecraft.state.velocity.normalize()
    h = r.cross(v)
    t = h.cross(r)

    ECI2Body = spacecraft.state.quaternion
    ECI2LVLH = Matrix( t, -1*h, -1*r ).transpose().toQuaternion()
    LVLH2Body = ECI2Body - ECI2LVLH
    
    return LVLH2Body

def ideal_nadircontroller_function(spacecraft: Spacecraft, args):
    control_torques = Vector(0, 0, 0)
    if len(spacecraft.recorder['State']) > 1:
        qError = LVLHqerror_function(spacecraft, args)

        rate = spacecraft.state.velocity.magnitude()/spacecraft.state.position.magnitude()
        rate0 = spacecraft.recorder['State'][-1].velocity.magnitude() / spacecraft.recorder['State'][-1].position.magnitude()

        time = spacecraft.system.datenow()
        time0 = spacecraft.recorder['Datetime'][-1]

        wRef = Vector(0, -1*rate, 0)
        wRef0 = Vector(0, -1*rate0, 0)
        DwRef = (wRef - wRef0) / (time - time0).total_seconds()
        w = spacecraft.state.bodyrate
        wError = w - wRef

        MRP = Vector(qError.x, qError.y, qError.z) / (1 + qError.w)
        I = spacecraft.inertia

        if MRP.magnitude()**2 > 1:
            MRP = -1 * MRP / (MRP.magnitude()**2)

        diag = Matrix( Vector(args[0], 0, 0), 
                       Vector(0, args[1], 0),
                       Vector(0, 0, args[2]))

        control_torques = -args[3] * MRP - diag * wError + I * (DwRef - w.cross(wRef)) + wRef.cross(I * w)
    return control_torques

def ideal_elevationsensor_function(spacecraft: Spacecraft, args):

    station = args[0]
    system = spacecraft.system
    gmst_ = system.gmst + system.time*(360.98564724)/(24*3600) 

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

    position = spacecraft.state.position

    target2pos = position - target

    angle = math.acos( (target.normalize() * target2pos.normalize()).sum() ) * R2D
    angle = 90 - angle

    return angle

ideal_magnetometer = Sensor('ideal_MTM')
ideal_magnetometer.setMethod(IDEAL_magnetometer_function)

ideal_bdotcontroller = Controller('ideal_BDOT')
ideal_bdotcontroller.setMethod(IDEAL_bdotcontroller_function, [5e5])

ideal_magnetorquer = Actuator('ideal_MTQ')
ideal_magnetorquer.setMethod(ideal_magnetorquer_function)

ideal_sunsensor = Sensor('ideal_SS')
ideal_sunsensor.setMethod(ideal_sunsensor_function)

ideal_nadircontroller = Controller('ideal_NADIR')
ideal_nadircontroller.setMethod(ideal_nadircontroller_function, [3e-4, 3e-4, 3e-4, 2e-4])

pedro_station = GroundStation('PEDRO', 14.647219, 121.07195333, 5)
davao_station = GroundStation('DVO_GRS', 7.125278, 125.645833, 5)

ideal_elevationsensor = Sensor('ideal_ELEV')
ideal_elevationsensor.setMethod(ideal_elevationsensor_function, [pedro_station])