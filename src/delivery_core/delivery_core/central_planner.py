import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import math
import random
import time

class CentralPlannerNode(Node):
    def __init__(self):
        super().__init__('central_planner')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
        self.arm_pub = self.create_publisher(JointTrajectory, '/arm_controller/joint_trajectory', 10)
        self.gripper_pub = self.create_publisher(JointTrajectory, '/gripper_controller/joint_trajectory', 10)
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        self.pickup_zones = {
            'Wheels': [0.5, 0.7, math.pi/2, 'North Wall (Right)'],
            'Shampoo': [-0.5, 0.7, math.pi/2, 'North Wall (Left)'],
            'Engine': [0.7, 0.5, 0.0, 'East Wall (Top)'],
            'Laptop': [0.7, -0.5, 0.0, 'East Wall (Bottom)']
        }
        self.delivery_station = [0.5, 0.5, 0.0] 
        
        # HOME BASE
        self.home_station = [-0.5, -0.2, 0.0] 
        self.order_queue = ['Wheels', 'Shampoo', 'Engine', 'Laptop']
        random.shuffle(self.order_queue)
        self.target_item = None
        self.state = 'WAITING' 
        self.start_time = time.time()
        self.grab_step = 0
        self.grab_timer = 0.0
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Central Planner Online. Waiting 50 seconds for facility map...")

    def euler_from_quaternion(self, x, y, z, w):
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        return math.atan2(t3, t4)

    def odom_callback(self, msg):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.current_yaw = self.euler_from_quaternion(q.x, q.y, q.z, q.w)

    def normalize_angle(self, angle):
        while angle > math.pi: angle -= 2.0 * math.pi
        while angle < -math.pi: angle += 2.0 * math.pi
        return angle

    def send_arm_pose(self, joint_angles, duration_sec):
        msg = JointTrajectory()
        msg.joint_names = ['joint1', 'joint2', 'joint3', 'joint4']
        point = JointTrajectoryPoint()
        point.positions = joint_angles
        point.velocities = [0.0, 0.0, 0.0, 0.0]
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        msg.points.append(point)
        self.arm_pub.publish(msg)

    def send_gripper_pose(self, position, duration_sec):
        msg = JointTrajectory()
        msg.joint_names = ['gripper'] 
        point = JointTrajectoryPoint()
        point.positions = [position]
        point.velocities = [0.0]
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        msg.points.append(point)
        self.gripper_pub.publish(msg)

    def control_loop(self):
        # 1. WAIT FOR DETECTOR
        if self.state == 'WAITING':
            if time.time() - self.start_time > 50.0:
                self.target_item = self.order_queue.pop(0) 
                self.get_logger().info(f"*** FIRST ORDER RECEIVED: {self.target_item} ***")
                self.state = 'DRIVING'
            return

        # 2. DRIVE TO TARGET
        if self.state == 'DRIVING':
            target_x, target_y, target_yaw, _ = self.pickup_zones[self.target_item]
            self.navigate_to(target_x, target_y, target_yaw, 'GRABBING')
            return

        # 3. ARM KINEMATICS SEQUENCE (PICKUP)
        if self.state == 'GRABBING':
            if self.grab_step == 0:
                self.get_logger().info("Opening Gripper & Reaching out...")
                self.send_gripper_pose(0.01, 1) # Full Open
                self.send_arm_pose([0.0, 0.4, 0.3, -0.7], 2) 
                self.grab_timer = time.time()
                self.grab_step = 1
            
            elif self.grab_step == 1 and (time.time() - self.grab_timer > 3.0):
                self.get_logger().info("Closing Gripper...")
                self.send_gripper_pose(-0.01, 1) # Close tightly
                self.grab_timer = time.time()
                self.grab_step = 2
                
            elif self.grab_step == 2 and (time.time() - self.grab_timer > 2.0):
                self.get_logger().info("Tucking arm safely for transit...")
                self.send_arm_pose([0.0, -1.0, 0.3, 0.7], 2) 
                self.grab_timer = time.time()
                self.grab_step = 3
                
            elif self.grab_step == 3 and (time.time() - self.grab_timer > 2.5):
                self.get_logger().info("Item secured! Returning to Delivery Station...")
                self.state = 'RETURNING'
            return

        # 4. RETURN TO DELIVERY STATION (Blue Box)
        if self.state == 'RETURNING':
            target_x, target_y, target_yaw = self.delivery_station
            self.navigate_to(target_x, target_y, target_yaw, 'DONE')
            return
            
        # 5. ARM KINEMATICS SEQUENCE (UNLOADING)
        if self.state == 'DONE':
            self.get_logger().info("*** DELIVERY ARRIVED! Reaching out to drop item... ***")
            self.send_arm_pose([0.0, 0.4, 0.3, -0.7], 2) 
            self.grab_timer = time.time()
            self.grab_step = 0
            self.state = 'UNLOADING'
            return
            
        if self.state == 'UNLOADING':
            if self.grab_step == 0 and (time.time() - self.grab_timer > 2.5):
                self.get_logger().info("Opening Gripper to release item...")
                self.send_gripper_pose(0.01, 1) # Full Open to drop
                self.grab_timer = time.time()
                self.grab_step = 1
                
            elif self.grab_step == 1 and (time.time() - self.grab_timer > 1.5):
                self.get_logger().info("Tucking arm back...")
                self.send_arm_pose([0.0, -1.0, 0.3, 0.7], 2) 
                self.grab_timer = time.time()
                self.grab_step = 2
                
            elif self.grab_step == 2 and (time.time() - self.grab_timer > 2.5):
                if len(self.order_queue) > 0:
                    self.target_item = self.order_queue.pop(0)
                    self.get_logger().info(f"*** NEXT ORDER QUEUED: {self.target_item} ***")
                    self.grab_step = 0 # Reset arm sequence
                    self.state = 'DRIVING'
                else:
                    self.get_logger().info("!!! ALL ORDERS DELIVERED. RETURNING TO HOME BASE !!!")
                    self.state = 'RETURNING_HOME'
            return

        # 6. DRIVE TO HOME BASE
        if self.state == 'RETURNING_HOME':
            target_x, target_y, target_yaw = self.home_station
            self.navigate_to(target_x, target_y, target_yaw, 'FINISHED')
            return

        # 7. POWER DOWN
        if self.state == 'FINISHED':
            self.get_logger().info("!!! MISSION ACCOMPLISHED. DELIVERER BOT PARKED AND POWERED DOWN !!!")
            # Send one last empty Twist message to guarantee the brakes are engaged
            msg = Twist()
            self.cmd_pub.publish(msg)
            self.state = 'OFF'
            return
        if self.state == 'OFF':
            return

    # Extracted navigation logic
    def navigate_to(self, target_x, target_y, target_yaw, next_state):
        dist_to_target = math.sqrt((target_x - self.current_x)**2 + (target_y - self.current_y)**2)
        angle_to_target = math.atan2(target_y - self.current_y, target_x - self.current_x)
        angle_error = self.normalize_angle(angle_to_target - self.current_yaw)

        msg = Twist()
        if dist_to_target > 0.05:
            if abs(angle_error) > 0.1:
                msg.angular.z = 0.4 if angle_error > 0 else -0.4
            else:
                msg.linear.x = 0.15 
        else:
            yaw_error = self.normalize_angle(target_yaw - self.current_yaw)
            if abs(yaw_error) > 0.1:
                msg.angular.z = 0.4 if yaw_error > 0 else -0.4
            else:
                msg.linear.x = 0.0
                msg.angular.z = 0.0
                self.cmd_pub.publish(msg)
                self.state = next_state
                return
        self.cmd_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = CentralPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()