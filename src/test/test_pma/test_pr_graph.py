import unittest
from pma import pr_graph

class TestPRGraph(unittest.TestCase):
    # TODO
    def test_goal_test(self):
        d_c = {
            'Action moveto 20':
                '(?robot - Robot ?start - RobotPose ?end - RobotPose)\
    			 (and \
                    (RobotAt ?robot ?start) \
    				(forall (?obj - Can) \
                        (not (Obstructs ?robot ?start ?obj))\
                    )\
    			)\
    		 	(and \
                    (not (RobotAt ?robot ?start)) \
    				(RobotAt ?robot ?end)\
    			) 0:0 0:19 19:19 19:19',
            'Action putdown 20': '(?robot - Robot ?can - Can ?target - Target ?pdp - RobotPose)\
				(and \
                    (RobotAt ?robot ?pdp) \
                    (IsPDP ?robot ?pdp ?target) \
                    (InGripper ?can)  \
    				(forall (?obj - Can) \
                        (not (At ?obj ?target)) \
                    ) \
                    (forall (?obj - Can) \
                        (not (Obstructs ?robot ?pdp ?obj))\
                    )\
                ) \
                (and \
                    (At ?can ?target)\
                    (not (InGripper ?can))\
                ) 0:0 0:0 0:0 0:0 0:19 19:19 19:19',
            'Derived Predicates': 'At, Can, Target; \
                RobotAt, Robot, RobotPose; \
                InGripper, Can; \
                IsGP, Robot, RobotPose, Can; \
                IsPDP, Robot, RobotPose, Target; \
                Obstructs, Robot, RobotPose, Can',
            'Attribute Import Paths': 'RedCircle core.util_classes.circle, \
                BlueCircle core.util_classes.circle, \
                GreenCircle core.util_classes.circle, \
                Vector2d core.util_classes.matrix, \
                GridWorldViewer core.util_classes.viewer',
            'Predicates Import Path':
                'core.util_classes.common_predicates',
            'Primitive Predicates':
                'geom, Can, RedCircle; \
                pose, Can, Vector2d; \
                geom, Target, BlueCircle; \
                pose, Target, Vector2d; \
                value, RobotPose, Vector2d; \
                geom, Robot, GreenCircle; \
                pose, Robot, Vector2d; \
                pose, Workspace, Vector2d; \
                w, Workspace, int; \
                h, Workspace, int; \
                size, Workspace, int; \
                viewer, Workspace, GridWorldViewer',
            'Action grasp 20': '(?robot - Robot ?can - Can ?target - Target ?gp - RobotPose)\
				(and \
                    (At ?can ?target) \
					(RobotAt ?robot ?gp)\
					(IsGP ?robot ?gp ?can)\
					(forall (?obj - Can) \
						(not (InGripper ?obj))\
					) \
					(forall (?obj - Can) \
						(not (Obstructs ?robot ?gp ?obj))\
					)\
				) \
				(and \
                    (not (At ?can ?target)) \
					(InGripper ?can) \
					(forall (?sym - RobotPose)\
					(not (Obstructs ?robot ?sym ?can)))\
				) 0:0 0:0 0:0 0:0 0:19 19:19 19:19 19:19',
    		'Types':
                'Can, Target, RobotPose, Robot, Workspace'}
        p_c = {
            'Init':
                '(geom target0 1), \
                (pose target0 [3,5]), \
                (value pdp_target0 [3,7.05]), \
                (geom target1 1), \
                (pose target1 [3,2]), \
                (value pdp_target1 [3,4.05]), \
                (geom target2 1), \
                (pose target2 [5,3]), \
                (value pdp_target2 [5,5.05]), \
                (geom can0 1), \
                (pose can0 [3,5]), \
                (value gp_can0 [5.05,5]), \
                (geom can1 1), \
                (pose can1 [3,2]), \
                (value gp_can1 [5.05,2]), \
                (geom pr2 1), \
                (pose pr2 [0,7]), \
                (value robot_init_pose [0,7]),\
                (pose ws [0,0]), \
                (w ws 8), \
                (h ws 9), \
                (size ws 1), \
                (viewer ws); \
                (At can0 target0), \
                (IsGP pr2 gp_can0 can0), \
                (At can1 target1), \
                (IsGP pr2 gp_can1 can1), \
                (IsPDP pr2 pdp_target0 target0), \
                (IsPDP pr2 pdp_target1 target1), \
                (IsPDP pr2 pdp_target2 target2), \
                (RobotAt pr2 robot_init_pose)',
    		'Objects': 'Target (name target0); \
    			RobotPose (name pdp_target0); \
    			Can (name can0); \
    			RobotPose (name gp_can0); \
    			Target (name target1); \
    			RobotPose (name pdp_target1); \
    			Can (name can1); \
    			RobotPose (name gp_can1); \
    			Target (name target2); \
    			RobotPose (name pdp_target2); \
    			Robot (name pr2); \
    			RobotPose (name robot_init_pose); \
    			Workspace (name ws)',
    		'Goal':
                '(At can0 target0), \
                (At can1 target1)'}
        s_c = {'LLSolver': 'NAMOSolver', 'HLSolver': 'FFSolver'}
        plan, msg = pr_graph.p_mod_abs(d_c, p_c, s_c)
        self.assertFalse(plan)
        self.assertEqual(msg, "Goal is already satisfied. No planning done.")

if __name__ == '__main__':
    unittest.main()
