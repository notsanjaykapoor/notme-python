import logging
import logging.config

import coloredlogs

LOG_LEVEL: str = "DEBUG"

FORMAT: str = "%(asctime)s - %(name)s - %(message)s"
# FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# FORMAT: str = "%(asctime)s - %(levelname)s - %(message)s"

# grey = "\x1b[38;20m"
# yellow = "\x1b[33;20m"
# red = "\x1b[31;20m"
# bold_red = "\x1b[31;1m"
# reset = "\x1b[0m"
#
# FORMATS = {
#   logging.DEBUG: f"{grey} + {format} + {reset}",
#   logging.INFO: f"{grey} + {format} + {reset}",
#   logging.WARNING: f"{yellow} + {format} + {reset}",
#   logging.ERROR: f"{red} + {format} + {reset}",
#   logging.CRITICAL: f"{bold_red} + {format} + {reset}",
# }

logging_config = {
    "version": 1,  # mandatory field
    # if you want to overwrite existing loggers' configs
    # "disable_existing_loggers": False,
    "formatters": {
        "basic": {
            "format": FORMAT,
        }
    },
    "handlers": {
        "cli": {  # deprecated?
            "formatter": "basic",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "level": LOG_LEVEL,
        },
        "console": {
            "formatter": "basic",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "level": LOG_LEVEL,
        },
    },
    "loggers": {
        "actor": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "api": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "app": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "cli": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "console": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "gql": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "service": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
        "strawberry.execution": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            # "propagate": False
        },
    },
}


def init(name: str):
    logging.config.dictConfig(logging_config)

    logger = logging.getLogger(name)

    coloredlogs.install(level="DEBUG", logger=logger, milliseconds=True, fmt=FORMAT)

    return logger
