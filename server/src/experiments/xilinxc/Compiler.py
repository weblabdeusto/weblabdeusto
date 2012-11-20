
import subprocess

# xst -intstyle ise -ifn "C:/pfc/PruebaWL/Untitled.xst" -ofn "C:/pfc/PruebaWL/Untitled.syr"

process = subprocess.Popen(["xst", "-intstyle", "ise", "-ifn", "C:/pfc/PruebaWL/Untitled.xst", 
                            "-ofn", "C:/pfc/PruebaWL/Untitled.syr"], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd = "C:\pfc\PruebaWL")
so, se = process.communicate(input)
#lines = process.stdout.readlines()

#print lines

print so, se

print "Good bye"