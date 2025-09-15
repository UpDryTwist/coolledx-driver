# Connection Improvements for CoolLEDX Driver

## Overview

This document describes the improvements made to handle Bluetooth connection errors more gracefully in the CoolLEDX driver, specifically addressing the `TimeoutError` and `asyncio.CancelledError` issues that can occur during sign updates.

## Problem Analysis

The original error showed:
```
asyncio.exceptions.CancelledError
...
TimeoutError
Error: Failed to update LED sign
```

### Root Causes

1. **Insufficient Exception Handling**: The code only caught `BleakError` but not `TimeoutError` or `asyncio.CancelledError`
2. **Poor Error Messages**: Generic "Failed to update LED sign" message provided no actionable information
3. **Fixed Timeouts**: No way to adjust connection timeouts for different environments
4. **Limited Logging**: Default INFO level logging didn't show enough detail for troubleshooting

## Improvements Made

### 1. Enhanced Exception Handling

**File**: `utils/tweak_sign.py`

- Added comprehensive exception handling for `TimeoutError`, `BleakError`, and `asyncio.CancelledError`
- Created `handle_connection_error()` function with specific error messages and troubleshooting suggestions
- Added graceful handling of keyboard interrupts

**File**: `src/coolledx/client.py`

- Updated connection retry logic to catch all relevant exception types
- Added informative retry messages with remaining attempt counts

### 2. Configurable Connection Parameters

**File**: `src/coolledx/argparser.py`

Added new command line arguments:
- `--connection-timeout`: Timeout in seconds for Bluetooth connection attempts (default: 10.0)
- `--connection-retries`: Number of connection retry attempts (default: 5)

### 3. Improved Logging and User Feedback

**File**: `utils/tweak_sign.py`

- Enhanced logging format with timestamps and module names
- Added INFO-level logging for each command being sent
- Provided specific error messages with troubleshooting suggestions
- Added success confirmation messages

### 4. Better Error Messages

The new error handling provides specific guidance based on the error type:

#### TimeoutError
```
Error: Connection timed out while connecting to device FF:FF:00:00:B7:C0
Suggestions:
  - Ensure the LED sign is powered on and in range
  - Check that the MAC address is correct
  - Try moving closer to the device
  - Ensure no other devices are connected to the sign
```

#### BleakError
```
Error: Bluetooth communication failed - [specific error]
Suggestions:
  - Check that Bluetooth is enabled on your system
  - Ensure the LED sign is not connected to another device
  - Try restarting the LED sign
  - Check system Bluetooth permissions
```

#### CancelledError
```
Error: Connection was cancelled or interrupted
Suggestions:
  - Try running the command again
  - Ensure stable Bluetooth connection
```

## Usage Examples

### Basic Usage (unchanged)
```bash
python utils/tweak_sign.py -t "Hello World"
```

### With Custom Timeout and Retries
```bash
# Increase timeout for difficult environments
python utils/tweak_sign.py -t "Hello World" --connection-timeout 20.0

# Reduce retries for faster failure
python utils/tweak_sign.py -t "Hello World" --connection-retries 2

# Debug mode for troubleshooting
python utils/tweak_sign.py -t "Hello World" --log DEBUG
```

### Docker Environment
For Docker environments where Bluetooth can be more challenging:
```bash
python utils/tweak_sign.py -t "Hello World" \
  --connection-timeout 30.0 \
  --connection-retries 10 \
  --log DEBUG
```

## Testing

A test script `utils/test_connection_improvements.py` has been created to verify the improvements work correctly. It tests:

1. TimeoutError handling
2. CancelledError handling  
3. Retry logic functionality

Run the tests with:
```bash
cd utils
python test_connection_improvements.py
```

## Troubleshooting Guide

### Connection Timeouts
1. **Increase timeout**: Use `--connection-timeout 20.0` or higher
2. **Check device power**: Ensure the LED sign is powered on
3. **Check range**: Move closer to the device
4. **Check interference**: Ensure no other Bluetooth devices are interfering

### Connection Cancelled
1. **System resources**: Check if system is under high load
2. **Bluetooth stack**: Restart Bluetooth service if possible
3. **USB Bluetooth**: Try unplugging and reconnecting USB Bluetooth adapters

### Repeated Failures
1. **Use debug logging**: Add `--log DEBUG` to see detailed connection attempts
2. **Increase retries**: Use `--connection-retries 10` for unstable environments
3. **Check device status**: Ensure the LED sign isn't connected to another device

## Future Improvements

Potential future enhancements could include:

1. **Exponential backoff**: Implement increasing delays between retry attempts
2. **Connection health monitoring**: Track connection stability over time
3. **Device discovery improvements**: Better handling of device scanning failures
4. **Configuration file support**: Allow saving connection parameters in a config file
5. **Connection pooling**: Reuse connections for multiple commands

## Backward Compatibility

All changes are backward compatible. Existing scripts and commands will continue to work without modification, but will benefit from the improved error handling and logging.
