import copy
import os
import sys
from appdirs import user_data_dir

LINUX = 1
DARWIN = 2
WINDOWS = 3

if sys.platform.startswith("darwin"):
    platform = DARWIN
    default_download_directory = os.path.join(os.path.expanduser("~"), 'Downloads')
    default_data_dir = user_data_dir("LBRY")
    default_lbryum_dir = os.path.join(os.path.expanduser("~"), ".lbryum")
elif sys.platform.startswith("win"):
    platform = WINDOWS
    from lbrynet.winhelpers.knownpaths import get_path, FOLDERID, UserHandle
    default_download_directory = get_path(FOLDERID.Downloads, UserHandle.current)
    default_data_dir = os.path.join(get_path(FOLDERID.RoamingAppData, UserHandle.current), "lbrynet")
    default_lbryum_dir = os.path.join(get_path(FOLDERID.RoamingAppData, UserHandle.current), "lbryum")
else:
    platform = LINUX
    default_download_directory = os.path.join(os.path.expanduser("~"), 'Downloads')
    default_data_dir = os.path.join(os.path.expanduser("~"), ".lbrynet")
    default_lbryum_dir = os.path.join(os.path.expanduser("~"), ".lbryum")


def convert_setting(setting, current_val):
    new_type = setting.__class__
    current_type = current_val.__class__
    if current_type is bool:
        if new_type is bool:
            return setting
        elif str(setting).lower() == "false":
            return False
        elif str(setting).lower() == "true":
            return True
        else:
            raise ValueError
    elif current_type is int:
        return int(setting)
    elif current_type is float:
        return float(setting)
    elif current_type is str:
        return str(setting)
    elif current_type is dict:
        return dict(setting)
    elif current_type is list:
        return list(setting)
    elif current_type is tuple:
        return tuple(setting)
    else:
        raise ValueError()


def convert_env_setting(setting, value):
    env_val = os.environ.get(setting, value)
    return convert_setting(env_val, value)


def get_env_settings(settings):
    for setting in settings:
        yield convert_env_setting(setting, settings[setting])


def add_env_settings_to_dict(settings_dict):
    for setting, env_setting in zip(settings_dict, get_env_settings(settings_dict)):
        settings_dict.update({setting: env_setting})
    return settings_dict


class Setting(object):
    __fixed = []
    __excluded = ['get_dict', 'update']

    def __iter__(self):
        for k in self.__dict__.iterkeys():
            if k.startswith('_') or k in self.__excluded:
                continue
            yield k

    def __getitem__(self, item):
        assert item in self, IndexError
        return self.__dict__[item]

    def __setitem__(self, key, value):
        assert key in self and key not in self.__fixed, KeyError(key)
        _value = convert_setting(value, self[key])
        self.__dict__.update({key: _value})

    def __contains__(self, item):
        return item in iter(self)

    def get_dict(self):
        return {k: self[k] for k in self}

    def update(self, other):
        for k, v in other.iteritems():
            try:
                self.__setitem__(k, v)
            except KeyError:
                pass
            except AssertionError:
                pass


class AdjustableSettings(Setting):
    def __init__(self):
        self.is_generous_host = True
        self.run_on_startup = False
        self.download_directory = default_download_directory
        self.max_upload = 0.0
        self.max_download = 0.0
        self.upload_log = True
        self.delete_blobs_on_remove = True
        self.use_upnp = True
        self.start_lbrycrdd = True
        self.run_reflector_server = False
        self.startup_scripts = []
        self.last_version = {'lbrynet': '0.0.1', 'lbryum': '0.0.1'}
        self.peer_port = 3333
        self.dht_node_port = 4444
        self.reflector_port = 5566
        self.download_timeout = 30
        self.max_search_results = 25
        self.search_timeout = 3.0
        self.cache_time = 150
        self.host_ui = True
        self.check_ui_requirements = True
        self.local_ui_path = False
        self.api_port = 5279
        self.search_servers = ['lighthouse1.lbry.io:50005']
        self.data_rate = .0001  # points/megabyte
        self.min_info_rate = .02  # points/1000 infos
        self.min_valuable_info_rate = .05  # points/1000 infos
        self.min_valuable_hash_rate = .05  # points/1000 infos
        self.max_connections_per_stream = 5
        self.known_dht_nodes = [('104.236.42.182', 4000),
                                ('lbrynet1.lbry.io', 4444),
                                ('lbrynet2.lbry.io', 4444),
                                ('lbrynet3.lbry.io', 4444)]
        self.pointtrader_server = 'http://127.0.0.1:2424'
        self.reflector_servers = [("reflector.lbry.io", 5566)]
        self.wallet = "lbryum"
        self.ui_branch = "master"
        self.default_ui_branch = 'master'
        self.data_dir = default_data_dir
        self.lbryum_wallet_dir = default_lbryum_dir
        self.use_auth_http = False
        self.sd_download_timeout = 3
        self.max_key_fee = {'USD': {'amount': 25.0, 'address': ''}}


class ApplicationSettings(Setting):
    def __init__(self):
        self.MAX_HANDSHAKE_SIZE = 2**16
        self.MAX_REQUEST_SIZE = 2**16
        self.MAX_BLOB_REQUEST_SIZE = 2**16
        self.MAX_RESPONSE_INFO_SIZE = 2**16
        self.MAX_BLOB_INFOS_TO_REQUEST = 20
        self.BLOBFILES_DIR = "blobfiles"
        self.BLOB_SIZE = 2**21
        self.LOG_FILE_NAME = "lbrynet.log"
        self.LOG_POST_URL = "https://lbry.io/log-upload"
        self.CRYPTSD_FILE_EXTENSION = ".cryptsd"
        self.API_INTERFACE = "localhost"
        self.API_ADDRESS = "lbryapi"
        self.ICON_PATH = "icons" if platform is WINDOWS else "app.icns"
        self.APP_NAME = "LBRY"
        self.PROTOCOL_PREFIX = "lbry"
        self.wallet_TYPES = ["lbryum", "lbrycrd"]
        self.SOURCE_TYPES = ['lbry_sd_hash', 'url', 'btih']
        self.CURRENCIES = {
                            'BTC': {'type': 'crypto'},
                            'LBC': {'type': 'crypto'},
                            'USD': {'type': 'fiat'},
        }
        self.LOGGLY_TOKEN = 'LJEzATH4AzRgAwxjAP00LwZ2YGx3MwVgZTMuBQZ3MQuxLmOv'
        self.ANALYTICS_ENDPOINT = 'https://api.segment.io/v1'
        self.ANALYTICS_TOKEN = 'Ax5LZzR1o3q3Z3WjATASDwR5rKyHH0qOIRIbLmMXn2H='


APPLICATION_SETTINGS = AdjustableSettings()
ADJUSTABLE_SETTINGS = AdjustableSettings()


class DefaultSettings(ApplicationSettings, AdjustableSettings):
    __fixed = APPLICATION_SETTINGS.get_dict().keys()

    def __init__(self):
        ApplicationSettings.__init__(self)
        AdjustableSettings.__init__(self)


DEFAULT_SETTINGS = DefaultSettings()


class Config(DefaultSettings):
    __shared_state = copy.deepcopy(DEFAULT_SETTINGS.get_dict())

    def __init__(self):
        self.__dict__ = add_env_settings_to_dict(self.__shared_state)

    @property
    def ORIGIN(self):
        return "http://%s:%i" % (DEFAULT_SETTINGS.API_INTERFACE, self.api_port)

    @property
    def REFERER(self):
        return "http://%s:%i/" % (DEFAULT_SETTINGS.API_INTERFACE, self.api_port)

    @property
    def API_CONNECTION_STRING(self):
        return "http://%s:%i/%s" % (DEFAULT_SETTINGS.API_INTERFACE, self.api_port, DEFAULT_SETTINGS.API_ADDRESS)

    @property
    def UI_ADDRESS(self):
        return "http://%s:%i" % (DEFAULT_SETTINGS.API_INTERFACE, self.api_port)
