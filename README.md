# Debugator — App Hive QA Continuous Automation Engine

High-speed, continuous Android QA automation engine for testing applications on **App Hive** (`com.codignia.apphive`), capturing guaranteed in-app screenshots, generating unique human feedback, and maximizing App Points (**UP**).

## Quick Start

1. Connect your Android device via USB with **USB Debugging** enabled:
   ```bash
   adb devices
   ```
2. Open App Hive on the phone.
3. Start the continuous conveyor-belt runner:
   ```bash
   python -u conveyor_qa.py
   ```

## Documentation & Handover

For complete setup instructions on a new machine, architectural details, gesture profiling, and troubleshooting, see **[`HANDOVER.md`](HANDOVER.md)**.
