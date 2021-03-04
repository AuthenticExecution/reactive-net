from enum import IntEnum

# Reactive Command codes
class ReactiveCommand(IntEnum):
    Connect             = 0x0
    Call                = 0x1
    RemoteOutput        = 0x2
    Load                = 0x3
    Ping                = 0x4
    RegisterEntrypoint  = 0x5
    Output              = 0x6 # called by software modules in SGX and Native
    RemoteRequest       = 0x7

    def has_response(self):
        if self == ReactiveCommand.RemoteOutput:
            return False
        if self == ReactiveCommand.Output:
            return False

        return True


# Reactive Result codes
class ReactiveResult(IntEnum):
    Ok                  = 0x0
    IllegalCommand      = 0x1
    IllegalPayload      = 0x2
    InternalError       = 0x3
    BadRequest          = 0x4
    CryptoError         = 0x5
    NotAttestedYet      = 0x6
    GenericError        = 0x7


# Reactive Entrypoint ids
class ReactiveEntrypoint(IntEnum):
    SetKey              = 0x0
    HandleInput         = 0x1
    HandleHandler       = 0x2
