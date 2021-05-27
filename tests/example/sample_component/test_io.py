"""
Sample test for showing how special IO operations can be handled.
"""
# nonDisruptive;dist

from tests.nd_parent_test import NdParentTest


class TestCase(NdParentTest):
    """
    The test case contains one function to test
    for glusterd service operations
    """

    def run_test(self, redant):
        """
        The purpose of this test case is for verifying the IO
        ops functions present in redant and also to give code
        references for people looking for inspiration of how to use
        an ops function. This test case will deal with the following
        flows,
        1. Using the special function for IO, create_deep_dirs_with_files.
        2. Performing a simple IO operation.
        """
        # Test the create_deep_dirs_with_files.
        async_obj = redant.create_deep_dirs_with_files(self.mountpoint, 1, 2,
                                                       3, 4, 10,
                                                       self.client_list[0])
        ret_dict = redant.wait_till_async_command_ends(async_obj)
        if ret_dict['error_code'] != 0:
            raise Exception(f"Failure : {ret_dict['error_msg']}")

        # Performing simple IO opreation.
        cmd = (f"ls {self.mountpoint}/*")
        ret_dict = redant.execute_abstract_op_node(cmd, self.client_list[0],
                                                   False)
        if ret_dict['error_code'] != 0:
            raise Exception(f"Failure : {ret_dict['error_msg']}")