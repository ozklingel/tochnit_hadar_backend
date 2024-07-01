
#! TODO: figure out why this script exists -> Ask Itzik
import subprocess

# Read the requirements.txt file
with open("requirements.txt", "r", encoding="utf-16") as file:
    packages = file.readlines()

list_problems = []
list_success = []
# Attempt to install each package individually
for package in packages:
    package = package.strip()
    try:
        subprocess.run(["pip", "install", package], check=True)
        list_success.append(package)
        print(f"Successfully installed {package}\n")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}, skipping.\n")
        list_problems.append(package)

print("Successfully installed packages:")
print(list_success)
print("Failed to install packages:")
print(list_problems)
