# Getting Started

## 0. Requirements

To follow this instruction you should have:

* ESP32-C3 device kit (e.g. ESP32-C3-DevKitM-1)
* Windows PC

## 1. Development environment setup (VS Code)

It is recommended to write and edit the code in **Visual Studio Code** (VS Code).

### 1.1 Installing Python

1. Download Python from the official site: https://www.python.org/downloads/
2. Run the installer.
3. **Important:** check the box **"Add Python to PATH"** during installation.
4. Click **Install Now** and wait for the installation to complete.
5. Verify the installation by opening a terminal (PowerShell) and running:

```powershell
python --version
```

You should see the installed Python version, e.g. `Python 3.12.4`.

### 1.2 Installing the Python extension for VS Code

1. Open VS Code.
2. Go to the **Extensions** panel (Ctrl+Shift+X).
3. In the search box type `Python`.
4. Find the extension **"Python"** by Microsoft (publisher: Microsoft) and click **Install**.
5. After installation, VS Code will automatically detect the installed Python interpreter.

This extension provides syntax highlighting, code completion, debugging, and other useful features for Python development.

### 1.3 Installing the Cline extension for VS Code

**Cline** is an AI assistant extension for VS Code that helps write, edit, and debug code directly in the editor.

1. Open VS Code.
2. Go to the **Extensions** panel (Ctrl+Shift+X).
3. In the search box type `Cline`.
4. Find the extension **"Cline"** and click **Install**.
5. After installation, the Cline icon will appear in the left activity bar.
6. Click the Cline icon and follow the setup wizard to configure the AI provider (API key, model, etc.).

Cline allows you to give tasks in natural language, and it will modify the project files, run commands, and explain the changes it makes.

## 2. Burning micropython into the ESP32 board

More details related to micropython could be found at [https://docs.micropython.org/en/latest/esp32/tutorial/intro.html](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html)

1. To burn micropython into ESP32 you should download esp-tool. Tool could be found here: https://github.com/espressif/esptool/ or downloaded via `python -m pip install esptool`
2. Connect board to the PC
3. With esp-tool erase current contents of flash `esptool.py --port COM4 erase_flash` (Note: port could be different)
4. Take micropython files from 'other' folder
5. Write downloaded firmware into ESP32 Flash: `esptool esp32c3 -p COM4 -b 460800 --before=default_reset --after=hard_reset --no-stub write_flash --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0 bootloader.bin 0x10000 micropython.bin 0x8000 partition-table.bin`
6. Open any Serial terminal with provided port above (`COM4`) and speed 115200, and press enter, you should see prompt `>>>`

## 3. Uploading firmware

1. Install `ampy` tool and `GitPython` library. (`python -m pip install adafruit-ampy` and `python -m pip install GitPython` )
2. Start `.\flash_p2.ps1 COM4 -force`
3. After you may open terminal and watch logs:

```logs
[  11481] [INFO] FW-UPD  Initialized  
[  11506] [INFO] WEBAPP  init done
```

If you see it, then device ready to work

## 4. Initial configuration

Now device ready to work. To configure network, you need connect to device Wi-Fi access point (will looks like `AR-[12 digits and letters]`, where the 12 characters are the hex representation of the device MAC address) and go to the http://192.168.4.1.
After a while, when device stops scanning Wi-Fi networks select yours, write the password of this network and press button `Connect`. Now you should have device connected to the yours Wi-Fi. 

## 5. Programming and debugging cycle

### 5.1 Writing changes to the ESP32

To write files to the device use the script:

```powershell
.\flash_p2.ps1 COM4
```

where **COM4** is the COM-port number to which the ESP32 is connected. Replace it with your own if needed (e.g. `COM3`, `COM5`, etc.).

By default `flash_p2.ps1` writes **only changed files**, which significantly speeds up the development cycle.

If you need to completely rewrite all files on the device, use the parameter:

```powershell
.\flash_p2.ps1 COM4 -force
```

After writing is complete, wait for the ESP32 to start automatically.

### 5.2 Standalone verification

To check the ESP32 operation without using Thonny:

1. Connect to the ESP32 access point.
2. Open the ESP32 Web interface in a browser.
3. Check the operation of the required functions.

For Web interface diagnostics it is recommended to use a browser on the computer.

Open **Developer Tools (F12)**:

- **Console** — JavaScript errors.
- **Network** — HTTP requests to the ESP32 and responses.
- **Response** — the content of the ESP32 response.

### 5.3 Viewing logs via Thonny

This step does not depend on the standalone verification and can be used right after flashing.

1. Connect the ESP32 via USB.
2. Launch Thonny.
3. Select the **MicroPython (ESP32)** interpreter and the required COM-port.
4. Open the **Shell**.

If the ESP32 is already running a program, **do not press Stop or Run**.

The Shell displays `print()` messages and diagnostic logs of the running program.

### 5.4 Interactive debugging

If you need to perform diagnostics manually:

1. Press **Stop**.
2. Wait for the prompt to appear:

```text
>>>
```

3. Execute commands via REPL, for example:

```python
import board
import gc

board.network.is_connected()
board.network.ifconfig()
board.network.scan()

gc.collect()
gc.mem_free()
```

If necessary, open the modified `.py` file and run it via **Run (F5)**.

## 6. Simulator start

To check protocol and other stuff, firmware could be started as python application itself:
```bash
$python3 src/main.py
```

Device web page will be available at port 3000 (http://localhost:3000)

