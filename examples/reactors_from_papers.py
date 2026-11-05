import paramak

# SPARC, from Figure 4 of "Overview of the SPARC tokamak" (2020)
sparc = paramak.sparc_from_2020_paper(rotation_angle=180)
sparc.export("sparc_from_2020_paper.step")
print("Saved as sparc_from_2020_paper.step")

# ITER, from the diagram in "ITER Project: International Cooperation and Energy Investment" (2020)
iter_reactor = paramak.iter_from_2020_paper(rotation_angle=180)
iter_reactor.export("iter_from_2020_paper.step")
print("Saved as iter_from_2020_paper.step")

# EU DEMO, from Figure 2 of "Definition of the basic DEMO tokamak geometry based on systems code studies" (2015)
eu_demo = paramak.eu_demo_from_2015_paper(rotation_angle=180)
eu_demo.export("eu_demo_from_2015_paper.step")
print("Saved as eu_demo_from_2015_paper.step")
