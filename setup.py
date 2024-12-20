from cx_Freeze import setup, Executable

script = "main.py" 

build_exe_options = {
    "packages": ["pandas", "numpy", 'cx_Frezze', "tkinter", "os", "cv2"],
    "includes": ["icon.ico"]
}

setup(
    name="Row-Tube Spreadsheet Generator",
    version="0.1.24",
    description="A program that given a heat exchanger image, it creates a spreadsheet based on quantity of rows and tubes.",
    author="Matheus Dumont Rosa",
    options={"build.exe": build_exe_options},
    executables=[Executable(script, base="Win32GUI", target_name="row_tube_spreadsheet_generator.exe", icon="icon.ico")],
)
