#!/usr/bin/env python3

import subprocess
import os

def getAnswer(text):
    try:
        return input(text)
    except KeyboardInterrupt:
        print("\nCtrl+C pressed, aborting")
        exit(-2)

print("Welcome to the Fugu14 iOS installer.")
print("This script will build and install Fugu14 on your device.")
print("Before continuing, please read the requirements:")
print("    - You need a supported device running a supported iOS version (see README.md)")
print("    - The device must be connected via USB")
print("    - You need the IPSW for your device, *unzipped*")
print("    - You need to have Xcode installed")
print("    - You need to have iproxy and ideviceinstaller installed (brew install usbmuxd ideviceinstaller)")

print(" Before building, please login to XCODE. Once done, put a file called DONE in the main folder")
from os.path import exists
import time
while True:
    if not exists("./DONE"):
        time.sleep(10)
    else
        break

csIdentity = "JDVQZVBU9X"
print("Patching arm/iOS/jailbreakd/build.sh...")
with open("arm/iOS/jailbreakd/build.sh", "r") as f:
    build_sh = f.read()

lines = []
for line in build_sh.split("\n"):
    if line.startswith("CODESIGN_IDENTITY="):
        lines.append(f'CODESIGN_IDENTITY="{csIdentity}"')
    else:
        lines.append(line)

with open("arm/iOS/jailbreakd/build.sh", "w") as f:
    f.write("\n".join(lines))

print("Patched")

print("Compiling jailbreakd...")

try:
    subprocess.run(["/bin/bash", "build.sh"], check=True, cwd="arm/iOS/jailbreakd/")
except subprocess.CalledProcessError as e:
    print(f"Failed to build jailbreakd! Exit status: {e.returncode}")
    exit(-1)

print("Successfully built jailbreakd")

print("Getting CDHash of jailbreakd...")
try:
    out = subprocess.run(["/usr/bin/codesign", "-dvvv", "arm/iOS/Fugu14App/Fugu14App/jailbreakd"], capture_output=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Failed to get CDHash of jailbreakd! Codesign exit status: {e.returncode}")
    print("stdout:")
    print(e.stdout)
    print("stderr:")
    print(e.stderr)
    exit(-1)

cdhash = None
out = out.stderr.decode("utf8")
for line in out.split("\n"):
    if line.startswith("CDHash="):
        cdhash = line[7:]
        break
        
if cdhash is None:
    print("Error: Codesign did not output the CDHash for jailbreakd!")
    exit(-1)

print(f"CDHash of jailbreakd: {cdhash}")

print("Patching arm/iOS/Fugu14App/Fugu14App/closures.swift...")

with open("arm/iOS/Fugu14App/Fugu14App/closures.swift", "r") as f:
    closure_swift = f.read()

lines = []
for line in closure_swift.split("\n"):
    if line.startswith('        try simpleSetenv("JAILBREAKD_CDHASH", '):
        lines.append (f'        try simpleSetenv("JAILBREAKD_CDHASH", "{cdhash}")')
    else:
        lines.append(line)

with open("arm/iOS/Fugu14App/Fugu14App/closures.swift", "w") as f:
    f.write("\n".join(lines))

print("Patched")

print("Compiling Fugu14App")

try:
    subprocess.run(["xcodebuild", "-scheme", "Fugu14App", "-derivedDataPath", "build","DEVELOPEMENT_TEAM=Y5QMTHQB49"], check=True, cwd="arm/iOS/Fugu14App/")
except subprocess.CalledProcessError as e:
    print(f"Failed to build Fugu14App! Exit status: {e.returncode}")
    print("If the build failed due to a codesign error, open arm/iOS/Fugu14App/Fugu14App.xcodeproj in Xcode")
    print("    and edit the Signing options in the Signing & Capabilities section.")
    exit(-1)

print("Successfully built Fugu14App")

print("Please open the folder containing your unzipped IPSW now.")

mntPath = "~/clone/tools"
print("Creating IPAs...")

try:
    subprocess.run(["/bin/bash", "build_ipas.sh", "../arm/iOS/Fugu14App/build/Build/Products/Release-iphoneos/Fugu14App.app", mntPath], check=True, cwd="tools")
except subprocess.CalledProcessError as e:
    print(f"Failed to create IPAs! Exit status: {e.returncode}")
    exit(-1)
print("IPAs created")
