// rustimport:pyo3

pub mod depth;
pub mod drive;
pub mod i2c_pwm;

use pyo3::prelude::*;

use std::thread::sleep;
use std::time::Duration;

use anyhow::{Context, Result};
use rppal::gpio::{Gpio, Level, Trigger};

use depth::Ultrasonic;
use drive::{Motors, Servo};
use i2c_pwm::init_i2c;

#[pyfunction]
fn reset_mcu() -> Result<()> {
    // We already know reset pin is 5 -> so skipping functions
    // let rst_pin: u8 = if check_board_type().expect("Error checking board type") {
    //     21
    // } else {
    //     5
    // };
    //   "RST": 16
    //  "MCURST":  5
    let mut mcu_rst_pin = Gpio::new()?.get(5)?.into_output();
    let mut rst_pin = Gpio::new()?.get(16)?.into_output();

    mcu_rst_pin.set_low();
    sleep(Duration::from_millis(1));
    mcu_rst_pin.set_high();
    sleep(Duration::from_millis(1));

    rst_pin.set_low();
    sleep(Duration::from_millis(1));
    rst_pin.set_high();
    sleep(Duration::from_millis(1));

    Ok(())
}

#[pyfunction]
pub fn reset_user() -> Result<bool> {
    let mut usr_rst_pin = Gpio::new()?.get(25)?.into_input();

    // Set up a rising edge trigger on pin 25
    usr_rst_pin
        .set_interrupt(Trigger::FallingEdge)
        .context("Setting Interrupt failed")?;

    let mut usr_out = false;

    // Monitor the USR button for a faling edge
    while let Ok(Some(Level::Low)) = usr_rst_pin.poll_interrupt(false, None) {
        usr_out = true;
    }

    Ok(usr_out)
}

#[pyfunction]
pub fn main_init() -> Result<()> {
    // RESET MCU
    reset_mcu().context("MCU RESET UNSUCCESSFULL [BEGIN]")?;
    // INIT I2C
    init_i2c().context("I2C INITIALIZATION FAILED")?;

    Ok(())
}

#[pyfunction]
pub fn servos_init() -> Result<[Servo; 3]> {
    let camera_servo_pin1 = Servo::new(0).context("camera_servo_pin1 init failed")?; // P0
    let camera_servo_pin2 = Servo::new(1).context("camera_servo_pin2 init failed")?; // P1
    let dir_servo_pin = Servo::new(2).context("dir_servo_pin init failed")?; // P2
    Ok([camera_servo_pin1, camera_servo_pin2, dir_servo_pin])
}

#[pyfunction]
pub fn motors_init(period: u16, prescaler: u16) -> Result<Motors> {
    let mut motors = Motors::new().context("motors init failed")?;
    // set period and prescaler for motors
    motors.left_motor.pwm.period(period)?;
    motors.left_motor.pwm.prescaler(prescaler)?;
    motors.right_motor.pwm.period(period)?;
    motors.right_motor.pwm.prescaler(prescaler)?;

    Ok(motors)
}

#[pyfunction]
pub fn ultrasonic_init() -> Result<Ultrasonic> {
    let ultrasonic = Ultrasonic::new().context("context")?;

    Ok(ultrasonic)
}
