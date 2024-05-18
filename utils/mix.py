#!/usr/bin/python3

#creates a colorful text message
#color mix can be specified using rgbymcwk as 2nd argument

import sys,os

if len(sys.argv)<2:
  print("-------------------------------------------------------------------------------")
  print("Usage: " + sys.argv[0] + " \"Text Message\" <rgbymcwk (optional color mix)> <optional args>")
  print("-------------------------------------------------------------------------------")
  sys.exit()

colors={
"r":"<#FF0000>",
"g":"<#00FF00>",
"b":"<#0000FF>", 
"y":"<#FFFF00>", 
"m":"<#FF00FF>", 
"c":"<#00FFFF>",
"w":"<#FFFFFF>",
"k":"<#000000>"
}
cidx='rgbymcw'
i=0
cmd="\""
text=sys.argv[1]
oidx=len(sys.argv)

if len(sys.argv)>2:
  j=True
  oidx=2
  for l in sys.argv[2]: 
    if 'rgbymcwk'.find(l)<0:
      j=False
      break;
  if j:
    cidx=sys.argv[2]
    oidx=3

for letter in text:
  if letter == ' ':
    cmd+=letter
  else:
    cmd+=colors[cidx[i]]+letter
    i+=1
    if i>len(cidx)-1:
      i=0

cmd+="\""
otherargs = ""
#print(sys.argv)
for a in range (oidx,len(sys.argv)):
  otherargs += " " + sys.argv[a]
cmd = "./tweak_sign.py -t " + cmd + otherargs
print(cmd)
os.system(cmd)
