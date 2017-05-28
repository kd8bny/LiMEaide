class Client(object):
    """Define client connection
    profile = {
        "distro": distro,
        "kver": kver,
        "arch": arch,
        "module": "lime.ko",
        "profile": "vol.zip"
        }
    """
    def __init__(self):
        super(Client, self).__init__
# Client specifics
        self.ip = None
        self.user = 'root'
        self.is_sudoer = False
        self.pass_ = None

# Profile and options
        self.profile = None
        self.output = 'dump.lime'
        self.output_dir = None
        self.compress = True
