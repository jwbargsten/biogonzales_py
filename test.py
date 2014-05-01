import biogonzales

p = biogonzales.Project()

print p.analysis_version
print p.conf()
print p.config
p.log.warn("errror")
