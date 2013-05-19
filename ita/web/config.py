session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'timeout': 60*60*5,
    'session.data_dir': './sessions',
    'session.auto': True
}


database = {
    "storage" : "sqlite",
    "path" : "test.db",
    "reset" : False
}

#database = {
#    "storage" : "mysql",
#    "user" : "root",
#    "password" : "",
#    "host" : "localhost",
#    "database" : "test"
#}           
