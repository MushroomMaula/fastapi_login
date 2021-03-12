if __name__ == "__main__":
    import os

    if os.path.exists(".env"):
        print(".env file already exists. Exiting...")
    else:
        with open(".env", "w") as f:
            f.write(f"SECRET={os.urandom(24).hex()}")
