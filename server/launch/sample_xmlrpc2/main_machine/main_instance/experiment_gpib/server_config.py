import os

######################
# GPIB configuration #
######################

fake_compiler_path    = "./tests/unit/weblab/experiment/devices/gpib/fake_compiler.py".replace('/',os.sep)
fake_linker_path    = "./tests/unit/weblab/experiment/devices/gpib/fake_linker.py".replace('/',os.sep)

# Real ones
#gpib_compiler_command = ['bcc32','-c','$CPP_FILE']
#gpib_linker_command   = ["ilink32","-Tpe","-c","$OBJ_FILE","c0x32,", "$EXE_FILE,",",","visa32","import32","cw32","bidsf"]

gpib_compiler_command = [ 'python', fake_compiler_path, '$CPP_FILE']

gpib_linker_command   = [ 
        'python',
        fake_linker_path, 
        #"ilink32", # ilink32 is the compiler itself
        "-Tpe", 
        "-c", 
        "$OBJ_FILE", 
        "c0x32,", 
        "$EXE_FILE,",
        ",", 
        "visa32", 
        "import32", 
        "cw32", 
        "bidsf"
    ]

