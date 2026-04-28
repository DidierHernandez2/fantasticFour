import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage


class WebcamNode(Node):
    def __init__(self):
        super().__init__("webcam_node")

        self.declare_parameter("camera_id", 0)
        camera_id = self.get_parameter("camera_id").value

        self.cap = cv2.VideoCapture(camera_id)
        self.pub = self.create_publisher(
            CompressedImage,
            "/camera/image/compressed",
            10,
        )

        self.timer = self.create_timer(0.05, self.publish_frame)
        self.get_logger().info("Webcam node iniciado")

    def publish_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        ok, encoded = cv2.imencode(".jpg", frame)
        if not ok:
            return

        msg = CompressedImage()
        msg.format = "jpeg"
        msg.data = encoded.tobytes()
        self.pub.publish(msg)

    def destroy_node(self):
        self.cap.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = WebcamNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()