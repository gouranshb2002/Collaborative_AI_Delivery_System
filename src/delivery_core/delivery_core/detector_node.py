import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class DetectorNode(Node):
    def __init__(self):
        super().__init__('detector_node')
        self.subscription = self.create_subscription(
            Image, '/detector_bot/camera/image_raw', self.image_callback, 10)
        self.bridge = CvBridge()
        # Load OpenCV's lightweight QR Code Scanner
        self.qr_detector = cv2.QRCodeDetector()
        self.get_logger().info("QR Scanner is Awake! Driving the robot to find products...")

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            # Detect and Decode QR Codes in the frame
            data, bbox, _ = self.qr_detector.detectAndDecode(cv_image)
            # If a QR code is found and contains text:
            if data:
                self.get_logger().info(f"*** DETECTED PRODUCT: {data} ***")
                # Draw a bright green box around the QR code
                if bbox is not None:
                    bbox = np.int32(bbox).reshape(-1, 2)
                    for i in range(len(bbox)):
                        cv2.line(cv_image, tuple(bbox[i]), tuple(bbox[(i+1) % len(bbox)]), (0, 255, 0), 3)
                # Write the product name on the screen
                cv2.putText(cv_image, f"FOUND: {data}", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.imshow("Detector Bot - QR Scanner Feed", cv_image)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()