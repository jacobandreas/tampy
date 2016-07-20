import numpy as np
from errors_exceptions import OpenRAVEException
from openravepy import quatFromAxisAngle, matrixFromPose, poseFromMatrix, \
axisAngleFromRotationMatrix, KinBody, GeometryType, RaveCreateRobot, \
RaveCreateKinBody, TriMesh, Environment
from core.util_classes.pr2 import PR2
from core.util_classes.can import Can, BlueCan, RedCan
from core.util_classes.circle import Circle, BlueCircle, RedCircle, GreenCircle
from core.util_classes.obstacle import Obstacle
from core.util_classes.wall import Wall
from core.util_classes.table import Table

WALL_THICKNESS = 1

class OpenRAVEBody(object):
    def __init__(self, env, name, geom):
        assert env is not None
        self.name = name
        self._env = env
        self._geom = geom
        if isinstance(geom, Circle):
            self._add_circle(geom)
        elif isinstance(geom, Can):
            self._add_can(geom)
        elif isinstance(geom, Obstacle):
            self._add_obstacle(geom)
        elif isinstance(geom, PR2):
            self._add_robot(geom)
        elif isinstance(geom, Table):
            self._add_table(geom)
        elif isinstance(geom, Wall):
            self._add_wall(geom)
        else:
            raise OpenRAVEException("Geometry not supported for %s for OpenRAVEBody"%geom)

    def delete(self):
        self._env.Remove(self.env_body)

    def set_transparency(self, transparency):
        for link in self.env_body.GetLinks():
            for geom in link.GetGeometries():
                geom.SetTransparency(transparency)


    def _add_circle(self, geom):
        color = [1,0,0]
        if hasattr(geom, "color") and geom.color == 'blue':
            color = [0, 0, 1]
        elif hasattr(geom, "color") and geom.color == 'green':
            color = [0, 1, 0]
        elif hasattr(geom, "color") and geom.color == 'red':
            color = [1, 0, 0]

        self.env_body = OpenRAVEBody.create_cylinder(self._env, self.name, np.eye(4),
                [geom.radius, 2], color)
        self._env.AddKinBody(self.env_body)

    def _add_can(self, geom):
        color = [1,0,0]
        if hasattr(geom, "color") and geom.color == 'blue':
            color = [0, 0, 1]
        elif hasattr(geom, "color") and geom.color == 'green':
            color = [0, 1, 0]
        elif hasattr(geom, "color") and geom.color == 'red':
            color = [1, 0, 0]

        self.env_body = OpenRAVEBody.create_cylinder(self._env, self.name, np.eye(4),
                [geom.radius, geom.height], color)
        self._env.AddKinBody(self.env_body)

    def _add_obstacle(self, geom):
        obstacles = np.matrix('-0.576036866359447, 0.918128654970760, 1;\
                        -0.806451612903226,-1.07017543859649, 1;\
                        1.01843317972350,-0.988304093567252, 1;\
                        0.640552995391705,0.906432748538011, 1;\
                        -0.576036866359447, 0.918128654970760, -1;\
                        -0.806451612903226,-1.07017543859649, -1;\
                        1.01843317972350,-0.988304093567252, -1;\
                        0.640552995391705,0.906432748538011, -1')

        body = RaveCreateKinBody(self._env, '')
        vertices = np.array(obstacles)
        indices = np.array([[0, 1, 2], [2, 3, 0], [4, 5, 6], [6, 7, 4], [0, 4, 5],
                            [0, 1, 5], [1, 2, 5], [5, 6, 2], [2, 3, 6], [6, 7, 3],
                            [0, 3, 7], [0, 4, 7]])
        body.InitFromTrimesh(trimesh=TriMesh(vertices, indices), draw=True)
        body.SetName(self.name)
        for link in body.GetLinks():
            for geom in link.GetGeometries():
                geom.SetDiffuseColor((.9, .9, .9))
        self.env_body = body
        self._env.AddKinBody(body)

    def _add_wall(self, geom):
        self.env_body = OpenRAVEBody.create_wall(self._env, geom.wall_type)
        self.env_body.SetName(self.name)
        self._env.Add(self.env_body)

    def _add_robot(self, geom):
        self.env_body = self._env.ReadRobotXMLFile(geom.shape)
        self.env_body.SetName(self.name)
        self._env.Add(self.env_body)

    def _add_table(self, geom):
        self.env_body = OpenRAVEBody.create_table(self._env, geom)
        self.env_body.SetName(self.name)
        self._env.Add(self.env_body)

    def set_pose(self, base_pose):
        trans = None
        if isinstance(self._geom, Circle) or isinstance(self._geom, Obstacle) or isinstance(self._geom, Wall):
            trans = OpenRAVEBody.base_pose_2D_to_mat(base_pose)
        elif isinstance(self._geom, PR2):
            trans = OpenRAVEBody.base_pose_to_mat(base_pose)
        elif isinstance(self._geom, Table) or isinstance(self._geom, Can):
            trans = OpenRAVEBody.base_pose_3D_to_mat(base_pose)
        self.env_body.SetTransform(trans)

    def set_dof(self, back_height, l_arm_pose, l_gripper, r_arm_pose, r_gripper):
        """
            This function assumed to be called when the self.env_body is a robot and its geom is type PR2
            It sets the DOF values for important joint of PR2

            back_height: back_height attribute of type Value
            l_arm_pose: l_arm_pose attribute of type Vector7d
            l_gripper: l_gripper attribute of type Value
            r_arm_pose: r_arm_pose attribute of type Vector7d
            r_gripper: r_gripper attribute of type Value
        """
        # Get current dof value for each joint
        dof_val = self.env_body.GetActiveDOFValues()
        # Obtain indices of left arm and right arm
        l_arm_inds = self.env_body.GetManipulator('leftarm').GetArmIndices()
        l_gripper_ind = self.env_body.GetJoint('l_gripper_l_finger_joint').GetDOFIndex()
        r_arm_inds = self.env_body.GetManipulator('rightarm').GetArmIndices()
        r_gripper_ind = self.env_body.GetJoint('torso_lift_joint').GetDOFIndex()
        b_height_ind = self.env_body.GetJoint('r_gripper_l_finger_joint').GetDOFIndex()
        # Update the DOF value
        dof_val[b_height_ind] = back_height
        dof_val[l_arm_inds], dof_val[l_gripper_ind] = l_arm_pose, l_gripper
        dof_val[r_arm_inds] ,dof_val[r_gripper_ind] = r_arm_pose, r_gripper
        # Set new DOF value to the robot
        self.env_body.SetActiveDOFValues(dof_val)

    @staticmethod
    def create_cylinder(env, body_name, t, dims, color=[0, 1, 1]):
        infocylinder = OpenRAVEBody.create_body_info(GeometryType.Cylinder, dims, color)
        if type(env) != Environment:
            import ipdb; ipdb.set_trace()
        cylinder = RaveCreateKinBody(env, '')
        cylinder.InitFromGeometries([infocylinder])
        cylinder.SetName(body_name)
        cylinder.SetTransform(t)
        return cylinder

    @staticmethod
    def create_box(env, name, transform, dims, color=[0,0,1]):
        infobox = OpenRAVEBody.create_box_info(dims, color, 0, True)
        box = RaveCreateKinBody(env,'')
        box.InitFromGeometries([infobox])
        box.SetName(name)
        box.SetTransform(transform)
        return box

    @staticmethod
    def create_body_info(body_type, dims, color, transparency = 0.0, visible = True):
        infobox = KinBody.Link.GeometryInfo()
        infobox._type = body_type
        infobox._vGeomData = dims
        infobox._bVisible = True
        infobox._fTransparency = 0
        infobox._vDiffuseColor = color
        return infobox

    @staticmethod
    def create_wall(env, wall_type):
        component_type = KinBody.Link.GeomType.Box
        wall_color = [0.5, 0.2, 0.1]
        box_infos = []
        if wall_type == 'closet':
            wall_endpoints = [[-1.0,-3.0],[-1.0,4.0],[1.9,4.0],[1.9,8.0],[5.0,8.0],[5.0,4.0],[8.0,4.0],[8.0,-3.0],[-1.0,-3.0]]
        else:
            raise NotImplemented
        for i, (start, end) in enumerate(zip(wall_endpoints[0:-1], wall_endpoints[1:])):
            dim_x, dim_y = 0, 0
            thickness = WALL_THICKNESS
            if start[0] == end[0]:
                ind_same, ind_diff = 0, 1
                length = abs(start[ind_diff] - end[ind_diff])
                dim_x, dim_y = thickness, length/2 + thickness
            elif start[1] == end[1]:
                ind_same, ind_diff = 1, 0
                length = abs(start[ind_diff] - end[ind_diff])
                dim_x, dim_y = length/2 + thickness, thickness
            else:
                raise NotImplemented, 'Can only create axis-aligned walls'

            transform = np.eye(4)
            transform[ind_same, 3] = start[ind_same]
            if start[ind_diff] < end[ind_diff]:
                transform[ind_diff, 3] = start[ind_diff] + length/2
            else:
                transform[ind_diff, 3] = end[ind_diff] + length/2
            dims = [dim_x, dim_y, 1]
            box_info = OpenRAVEBody.create_body_info(component_type, dims, wall_color)
            box_info._t = transform
            box_infos.append(box_info)
        wall = RaveCreateRobot(env, '')
        wall.InitFromGeometries(box_infos)
        return wall



    @staticmethod
    def create_table(env, geom):
        thickness = geom.thickness
        leg_height = geom.leg_height
        back = geom.back
        dim1, dim2 = geom.table_dim
        legdim1, legdim2 = geom.leg_dim

        table_color = [0.5, 0.2, 0.1]
        component_type = KinBody.Link.GeomType.Box
        tabletop = OpenRAVEBody.create_body_info(component_type, [dim1/2, dim2/2, thickness/2], table_color)

        leg1 = OpenRAVEBody.create_body_info(component_type, [legdim1/2, legdim2/2, leg_height/2], table_color)
        leg1._t[0, 3] = dim1/2 - legdim1/2
        leg1._t[1, 3] = dim2/2 - legdim2/2
        leg1._t[2, 3] = -leg_height/2 - thickness/2

        leg2 = OpenRAVEBody.create_body_info(component_type, [legdim1/2, legdim2/2, leg_height/2], table_color)
        leg2._t[0, 3] = dim1/2 - legdim1/2
        leg2._t[1, 3] = -dim2/2 + legdim2/2
        leg2._t[2, 3] = -leg_height/2 - thickness/2

        leg3 = OpenRAVEBody.create_body_info(component_type, [legdim1/2, legdim2/2, leg_height/2], table_color)
        leg3._t[0, 3] = -dim1/2 + legdim1/2
        leg3._t[1, 3] = dim2/2 - legdim2/2
        leg3._t[2, 3] = -leg_height/2 - thickness/2

        leg4 = OpenRAVEBody.create_body_info(component_type, [legdim1/2, legdim2/2, leg_height/2], table_color)
        leg4._t[0, 3] = -dim1/2 + legdim1/2
        leg4._t[1, 3] = -dim2/2 + legdim2/2
        leg4._t[2, 3] = -leg_height/2 - thickness/2

        if back:
            back_plate = OpenRAVEBody.create_body_info(component_type, [legdim1/10, dim2/2, leg_height-thickness/2], table_color)
            back_plate._t[0, 3] = dim1/2 - legdim1/10
            back_plate._t[1, 3] = 0
            back_plate._t[2, 3] = -leg_height/2 - thickness/4

        table = RaveCreateRobot(env, '')
        if not back:
            table.InitFromGeometries([tabletop, leg1, leg2, leg3, leg4])
        else:
            table.InitFromGeometries([tabletop, leg1, leg2, leg3, leg4, back_plate])
        return table

    @staticmethod
    def base_pose_2D_to_mat(pose):
        # x, y = pose
        assert len(pose) == 2
        x = pose[0]
        y = pose[1]
        rot = 0
        q = quatFromAxisAngle((0, 0, rot)).tolist()
        pos = [x, y, 0]
        # pos = np.vstack((x,y,np.zeros(1)))
        matrix = matrixFromPose(q + pos)
        return matrix

    @staticmethod
    def base_pose_3D_to_mat(pose):
        # x, y = pose
        assert len(pose) == 3
        x = pose[0]
        y = pose[1]
        z = pose[2]
        rot = 0
        q = quatFromAxisAngle((0, 0, rot)).tolist()
        pos = [x, y, z]
        # pos = np.vstack((x,y,np.zeros(1)))
        matrix = matrixFromPose(q + pos)
        return matrix

    @staticmethod
    def mat_to_base_pose_2D(mat):
        pose = poseFromMatrix(mat)
        x = pose[4]
        y = pose[5]
        return np.array([x,y])

    @staticmethod
    def base_pose_to_mat(pose):
        # x, y, rot = pose
        assert len(pose) == 3
        x = pose[0]
        y = pose[1]
        rot = pose[2]
        q = quatFromAxisAngle((0, 0, rot)).tolist()
        pos = [x, y, 0]
        # pos = np.vstack((x,y,np.zeros(1)))
        matrix = matrixFromPose(q + pos)
        return matrix

    @staticmethod
    def mat_to_base_pose(mat):
        pose = poseFromMatrix(mat)
        x = pose[4]
        y = pose[5]
        rot = axisAngleFromRotationMatrix(mat)[2]
        return np.array([x,y,rot])
