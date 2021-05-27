import traceback
import abc
from common.mixin import RedantMixin


class NdParentTest(metaclass=abc.ABCMeta):

    """
    This class contains the standard info and methods which are needed by
    most of the non disruptive test cases.

    TEST_RES: states the result of the test case

    """

    conv_dict = {
        "dist": "distributed",
        "rep": "replicated",
        "dist-rep": "distributed-replicated",
                    "disp": "dispersed",
                    "dist-disp": "distributed-dispersed",
                    "arb": "arbiter",
                    "dist-arb": "distributed-arbiter"
    }

    def __init__(self, mname: str, param_obj, volume_type: str,
                 env_obj, log_path: str, log_level: str = 'I'):
        """
        Initializing connection and logging.
        """

        server_details = param_obj.get_server_config()
        client_details = param_obj.get_client_config()
        self.TEST_RES = True
        self.volume_type = volume_type
        self.vol_type_inf = param_obj.get_volume_types()
        self._configure(f"{mname}-{volume_type}", server_details,
                        client_details, env_obj, log_path, log_level)
        self.server_list = param_obj.get_server_ip_list()
        self.client_list = param_obj.get_client_ip_list()
        self.brick_roots = param_obj.get_brick_roots()
        if self.volume_type != "Generic":
            self.vol_name = (f"redant-{volume_type}")
            self.mountpoint = (f"/mnt/{self.vol_name}")

    def _configure(self, mname: str, server_details: dict,
                   client_details: dict, env_obj, log_path: str,
                   log_level: str):
        self.redant = RedantMixin(server_details, client_details, env_obj)
        self.redant.init_logger(mname, log_path, log_level)
        self.redant.establish_connection()
        self.test_name = mname
        self.pre_test_env = env_obj

    @abc.abstractmethod
    def run_test(self, redant):
        pass

    def parent_run_test(self):
        """
        Function to handle the exception logic and invokes the run_test
        which is overridden by every TC.
        """
        try:
            self.run_test(self.redant)
        except Exception as error:
            tb = traceback.format_exc()
            self.redant.logger.error(error)
            self.redant.logger.error(tb)
            self.TEST_RES = False

    def terminate(self):
        """
        Closes connection and checks the env
        """
        # Check if the post_test env state is same as that of the
        # pre_test env state.
        if self.volume_type != "Generic":
            try:
                # Condition 1. Volume started state.
                vol_param = self.vol_type_inf[self.conv_dict[self.volume_type]]
                self.redant.sanitize_volume(self.vol_name, self.server_list,
                                            self.client_list, self.brick_roots,
                                            vol_param)

                # Condition 2. Volume options if set to be reset.
                self.redant.reset_volume_option(self.vol_name, 'all',
                                                self.server_list[0])
            except Exception as e:
                self.TEST_RES = False
                tb = traceback.format_exc()
                self.redant.logger.error(e)
                self.redant.logger.error(tb)
        self.redant.cleanup_brick_dirs()
        self.redant.deconstruct_connection()