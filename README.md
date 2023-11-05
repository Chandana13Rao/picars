# picars
Autonomous Vehicle using Raspberry Pi and PiCar-X kit created using Rust

# Folder Structure
```mermaid
graph TD;

  1[dust<br> Rust Picar-X binary]
  1 --> 1_1
  1 --> 1_2

  1_1[drishti<br> Image processing library]
  1_1 --> 1_1_1[depth<br> Ultrasonic sensor module]
  1_1 --> 1_1_2[eyes<br> Camera module]
  1_1 --> 1_1_3[lane<br> Lane module]

  1_2[vahana<br> Driving library]
  1_2 --> 1_2_2[drive<br> Motors and Servo module]

  2[ruspy<br> Rust Base Software]
  2 --> 1_1
  2 --> 1_2
  2 --> 3

 3[Python<br> Python frontend (ASW) with Rust Backend (BSW)]
```

# Pin Configuration

| Component | Pin (robot-hat) |
| :------- | :--------: |
| mcu_reset_pin | 5 |
| ultrasonic_trig_pin | D2 |
| ultrasonic_echo_pin | D3 |
| left_motor_dir_pin | D4 |
| right_motor_dir_pin | D5 |
| camera_servo_pin1 | P0 |
| camera_servo_pin2 | P1 |
| dir_servo_pin | P2 |
| left_motor_pwm_pin | P12 |
| right_motor_pwm_pin | P13 |


# Code statistics

```python
===============================================================================
 Language            Files        Lines         Code     Comments       Blanks
===============================================================================
 Python                 10         1709         1230          214          265
 TOML                    7           83           59            8           16
 Prolog                  1            8            8            0            0
-------------------------------------------------------------------------------
 Rust                   12         1795         1288          211          296
 |- Markdown             1            3            0            3            0
 (Total)                           1798         1288          214          296
-------------------------------------------------------------------------------
 Markdown                1           47            0           36           11
 |- Python               1           17           17            0            0
 (Total)                             64           17           36           11
===============================================================================
 Total                  31         3642         2585          469          588
===============================================================================
```
