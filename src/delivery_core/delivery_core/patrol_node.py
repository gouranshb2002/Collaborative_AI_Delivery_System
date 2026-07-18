import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math
import time

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        
        self.publisher = self.create_publisher(Twist, '/detector_bot/cmd_vel', 10)
        self.subscriber = self.create_subscription(Odometry, '/detector_bot/odom', self.odom_callback, 10)
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0
        
        # Format: [X, Y, Target_Yaw (Radians), Description]
        # math.pi/2 = North. 0.0 = East. None = Don't care.
        self.waypoints = [
            [0.2, -0.6, None, 'Detour: Navigating around Deliverer'],
            [-0.5, 0.4, math.pi/2, 'Looking at Shampoo (North Wall - Left)'],
            [0.5, 0.4, math.pi/2, 'Looking at Wheels (North Wall - Right)'],
            [0.4, 0.5, 0.0, 'Looking at Engine (East Wall - Left)'], 
            [0.4, -0.5, 0.0, 'Looking at Laptop (East Wall - Right)'],
            [0.2, -0.6, None, 'Detour: Navigating back to base'],
            [-0.5, -0.7, math.pi/2, 'Return to Resting Area (Center)'] 
        ]
        self.current_wp_index = 0
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Patrol Node Awake! Starting facility scan...")

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

    def control_loop(self):
        if self.current_wp_index >= len(self.waypoints):
            self.get_logger().info("Patrol Complete! Awaiting Central Planner command.")
            self.publisher.publish(Twist()) 
            self.timer.cancel()
            return

        target_x = self.waypoints[self.current_wp_index][0]
        target_y = self.waypoints[self.current_wp_index][1]
        target_yaw = self.waypoints[self.current_wp_index][2]
        desc = self.waypoints[self.current_wp_index][3]
        dist_to_target = math.sqrt((target_x - self.current_x)**2 + (target_y - self.current_y)**2)
        angle_to_target = math.atan2(target_y - self.current_y, target_x - self.current_x)
        angle_error = self.normalize_angle(angle_to_target - self.current_yaw)
        msg = Twist()

        if dist_to_target > 0.05:
            if abs(angle_error) > 0.1:
                # 1. Rotate towards target coordinate
                msg.angular.z = 0.5 if angle_error > 0 else -0.5
                msg.linear.x = 0.0
            else:
                # 2. Drive straight to target coordinate
                msg.linear.x = 0.2
                msg.angular.z = 0.0
        else:
            # 3. Coordinate Reached! Check if we need to turn to face the wall.
            if target_yaw is not None:
                yaw_error = self.normalize_angle(target_yaw - self.current_yaw)
                if abs(yaw_error) > 0.1:
                    # 4. Rotate to face the wall squarely
                    msg.angular.z = 0.5 if yaw_error > 0 else -0.5
                    msg.linear.x = 0.0
                    self.publisher.publish(msg)
                    return # Exit loop early so it keeps turning and doesn't sleep yet
            
            # 5. Target fully reached and aligned perfectly
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher.publish(msg) 
            
            if "Looking" in desc:
                self.get_logger().info(f"Aligned squarely with target: {desc}. Scanning...")
                time.sleep(3.0) 
            else:
                self.get_logger().info(f"Cleared Via Point: {desc}")
            self.current_wp_index += 1
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = PatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Manual stop engaged.")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()