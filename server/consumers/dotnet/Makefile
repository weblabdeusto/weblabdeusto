all:
	gmcs -t:library -out:LitJson.dll -warn:0 LitJson/*.cs
	gmcs -t:library -out:WebLabDeusto.dll -r:LitJson.dll WebLabDeusto/*.cs

sample: all
	gmcs -out:sample.exe -r:WebLabDeusto.dll Sample.cs 

run: 
	mono sample.exe

