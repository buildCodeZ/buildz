#

# type 1
confbd = ConfsBuilder()
confbd.add_build(EnvBuilder())
confsbd.add_build(DataBduiler())
confsbd.add_build(InitBuilder())
confsbd.add_build(VarBuilder())
confs = confsbd()

confbd = confsbd.build_conf()

conf = Conf()
conf.add_env()
conf.add_data()
conf.add_init()

confs.add_conf(conf)

# type2

mg = Manager()
mg.add("env", EnvBuilder())
mg.add("data", Data())

mg.data.add(id, Data())

mg.data.get()