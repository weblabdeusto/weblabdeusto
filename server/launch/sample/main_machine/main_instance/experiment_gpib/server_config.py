import os

######################
# GPIB configuration #
######################

compilers_path = './sample/etc/weblab/main_machine/main_instance/experiment_gpib/'

fake_compiler_path  = (compilers_path + "fake_compiler.py").replace('/',os.sep)
fake_linker_path    = (compilers_path + "fake_linker.py").replace('/',os.sep)

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

gpib_just_testing = True

gpib_public_output_file_filename = 'gpib.txt'
