class Config:

    APPNAME = "MagicPortKnocker"
    APPAUTHOR = "Bianca Ploch"

    # admin core
    DEFAULT_NUMBER_OF_TICKETS = 100
    ## range of acceptable ports
    PORT_MIN = 1
    PORT_MAX = 65535

    # cli client
    TICKETS_TO_TRY = 3
    NUMBER_OF_PACKET_RESENDS = 5

    # logger
    LOGGER_FNAME = "security.log"