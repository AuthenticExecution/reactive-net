from enum import IntEnum

class ReactiveCommand(IntEnum):
    Connect             = 0x0
    Call                = 0x1
    RemoteOutput        = 0x2
    Load                = 0x3
    Ping                = 0x4
    Output              = 0x5 # called by software modules in SGX and NoSGX

    def has_response(self):
        if self == CommandCode.RemoteOutput:
            return False
        if self == CommandCode.Output:
            return False

        return True


class ReactiveResult(IntEnum):
    Ok                  = 0x0
    IllegalCommand      = 0x1
    IllegalPayload      = 0x2
    InternalError       = 0x3
    BadRequest          = 0x4
    CryptoError         = 0x5
    GenericError        = 0x6


class ReactiveEntrypoint(IntEnum):
    SetKey              = 0x0
    HandleInput         = 0x1
