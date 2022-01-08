import os


class Utils:
    @staticmethod
    def _get_path_name() -> str:
        if os.path.basename(os.getcwd()) == "unittests":
            return os.getcwd()
        else:
            return f"{os.getcwd()}{os.sep}tests{os.sep}unittests"
