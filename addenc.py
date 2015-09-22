import os,os.path

for root,dirs,files in os.walk("tests"):
    for name in files:
        if name.endswith(".py"):
            fn=os.path.join(root,name)
            with open(fn,"rb") as f:
                lines=f.readlines()
            if lines:
                with open(fn,"wb") as f:
                    for l in lines:
                        f.write(l.replace(" "*8,"\t"))
            
    
