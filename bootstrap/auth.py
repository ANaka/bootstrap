from dotenv import load_dotenv


def set_environment_vars(method="dotenv"):
    if method == "dotenv":
        load_dotenv()
