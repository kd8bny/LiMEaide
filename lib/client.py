class Client:
    """All client attributes including the profile.

    The profile format is stored as json as such
    profile = {
        "distro": distro,
        "kver": kver,
        "arch": arch,
        "module": "lime.ko",
        "profile": "vol.zip"
        }
    """

    def __init__(self):
        super(Client, self).__init__()
        # Client specifics
        self.ip = None
        self.port = None
        self.transfer = 'network'
        self.user = 'root'
        self.is_sudoer = False
        self.pass_ = None
        self.job_name = None

        # Profile and options
        self.profile = None
        self.output = 'dump.lime'
        self.format = 'lime'
        self.digest = 'sha1'
        self.output_dir = None
        self.compress = True
        self.delay_pickup = False
