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
        self.user = None
        self.pass_ = None

        # LiME options
        self.output = None
        self.format = None
        self.digest = None

        # Profile and options
        self.profile = None
        self.output_dir = None
        self.compress = None
        self.delay_pickup = None
        self.job_name = None
