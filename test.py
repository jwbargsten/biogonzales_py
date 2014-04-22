import project

p = project.Project()

print p.analysis_version
print p.conf()
print p.config
p.log.warn("errror")
