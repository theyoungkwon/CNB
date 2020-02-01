import math

scale = 10


def handleIMU(imu_from_myo):
    quat = imu_from_myo[0]
    roll = math.atan2(2.0 * (quat.w * quat.x + quat.y * quat.z), 1.0 - 2.0 * (quat.x * quat.x + quat.y * quat.y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (quat.w * quat.y - quat.z * quat.x))))
    yaw = math.atan2(2.0 * (quat.w * quat.z + quat.x * quat.y), 1.0 - 2.0 * (quat.y * quat.y + quat.z * quat.z))

    return translate(roll, pitch, yaw)


def handleIMUArray(imu_array, _scale=None):
    w = imu_array[0]
    x = imu_array[1]
    y = imu_array[2]
    z = imu_array[3]

    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    return translate(roll, pitch, yaw, _scale)


def translate(roll, pitch, yaw, _scale=None):
    if _scale is None:
        _scale = scale
    roll_w = ((roll + math.pi) / (math.pi * 2.0) * _scale)
    pitch_w = ((pitch + math.pi / 2.0) / math.pi * _scale)
    yaw_w = ((yaw + math.pi) / (math.pi * 2.0) * _scale)

    return roll_w, pitch_w, yaw_w


def is_angle_between(target, angle1, angle2):
    rAngle = ((angle2 - angle1) % 360 + 360) % 360
    if rAngle >= 180:
        tmp = angle1
        angle1 = angle2
        angle2 = tmp

    if angle1 <= angle2:
        if target >= angle1 and target <= angle2:
            return (target - angle1) / rAngle
    else:
        if target >= angle1 or target <= angle2:
            return (target + 360 - angle1) % 360 / rAngle


if __name__ == '__main__':
    is_angle_between(10, 350, 20)
