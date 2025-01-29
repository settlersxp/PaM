from deployment_utils import register_logger, \
                                install_requirements, \
                                get_venv_path, \
                                create_and_install_venv

# Setup logging
logger = register_logger('setup_env')


def main():
    # setup virtual environment
    create_and_install_venv(logger)

    # get activate and python commands
    activate_cmd, python_cmd = get_venv_path(logger)

    # install requirements
    install_requirements(logger, activate_cmd, python_cmd)

    logger.info("Setup completed successfully!")


if __name__ == "__main__":
    main()
