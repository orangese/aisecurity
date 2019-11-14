"""

"aisecurity.samples.demo"

Demonstration of facial recognition system.

"""


def demo(model="ms_celeb_1m", path=None, use_log=True, use_dynamic=True, use_picam=False, use_graphics=True,
         resize=None, verbose=False):

    # default arg values (for Pycharm, where args.* default to None)
    if model is None:
        model = "ms_celeb_1m"
    if use_log is None:
        use_log = True
    if use_dynamic is None:
        use_dynamic = True
    if use_picam is None:
        use_picam = False
    if use_graphics is None:
        use_graphics = True
    if verbose is None:
        verbose = False

    if not verbose:
        # SETUP
        import os

        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

        # ERROR HANDLING
        import warnings

        warnings.simplefilter(action="ignore", category=FutureWarning)
        warnings.simplefilter(action="ignore", category=UserWarning)
        warnings.simplefilter(action="ignore", category=RuntimeWarning)

        import tensorflow as tf

        try:
            tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        except AttributeError:
            tf.logging.set_verbosity(tf.logging.ERROR)


    from aisecurity.facenet import FaceNet, retrieve_embeds, cprint
    from aisecurity.utils.paths import DATABASE, CONFIG_HOME


    cprint("\nLoading facial recognition system", attrs=["bold"], end="")
    cprint("...", attrs=["bold", "blink"])
    facenet = FaceNet(path if path else CONFIG_HOME + "/models/{}.h5".format(model))

    cprint("\nLoading encrypted database", attrs=["bold"], end="")
    cprint("...", attrs=["bold", "blink"])
    facenet.set_data(retrieve_embeds(DATABASE, encrypted="names"))

    input("\nPress ENTER to continue:")

    facenet.real_time_recognize(use_log=use_log, use_dynamic=use_dynamic, use_picam=use_picam,
                                use_graphics=use_graphics, resize=resize)


if __name__ == "__main__":
    import argparse

    def to_bool(string):
        if string.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif string.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("boolean value expected")

    def bounded_float(string):
        if 0. <= float(string) <= 1.:
            return float(string)
        else:
            raise argparse.ArgumentTypeError("float between 0 and 1 expected")

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="name of facenet model", type=str)
    parser.add_argument("--path_to_model", help="path to facenet model", type=str)
    parser.add_argument("--use_log", help="(boolean) use MySQL logging", type=to_bool)
    parser.add_argument("--use_dynamic", help="(boolean) use dynamic logging", type=to_bool)
    parser.add_argument("--use_picam", help="(boolean) use Picamera", type=to_bool)
    parser.add_argument("--use_graphics", help="(boolean) display graphics", type=to_bool)
    parser.add_argument("--resize", help="(boolean) resize frame for faster recognition", type=bounded_float)
    parser.add_argument("--verbose", help="(boolean) suppress warnings and TensorFlow output", type=to_bool)
    args = parser.parse_args()

    demo(model=args.model, path=args.path_to_model, use_log=args.use_log, use_dynamic=args.use_dynamic,
         use_picam=args.use_picam, use_graphics=args.use_picam, resize=args.resize, verbose=args.verbose)