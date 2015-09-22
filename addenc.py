import os,os.path,re

fu=re.compile("failUnless *[(](.+?) *== *(.+?) *,")
if False:
    for root,dirs,files in os.walk("tests"):
        for name in files:
            if name.endswith(".py"):
                fn=os.path.join(root,name)
                with open(fn,"rb") as f:
                    lines=f.readlines()
                if lines:
                    with open(fn,"wb") as f:
                        for l in lines:
                            l=l.replace("list(range(","range(")
                            f.write(l.replace(" "*8,"\t"))
            
    
