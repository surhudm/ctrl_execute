from eups import Eups


e = Eups()
setupProducts = e.getSetupProducts()
for i in setupProducts:
    print "setup -j %s %s" % (i.name, i.version)
