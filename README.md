# reactive-net
Python library for managing network communications

Network messages are of three types:

- `Message`
  - Format: `<size u16><payload>`
  - This is not used in practice
- `CommandMessage`
  - Format: `<code u16><size u16><payload>`
- `ResultMessage`
  - Format: `<code u8><size u16><payload>`



## Command Messages

```python
class ReactiveCommand(IntEnum):
    Connect             = 0x0
    Call                = 0x1
    RemoteOutput        = 0x2
    Load                = 0x3
    Ping                = 0x4
    RegisterEntrypoint  = 0x5
    Output              = 0x6 # called by software modules in SGX and Native
    RemoteRequest       = 0x7
```

- Not all the commands have a response! (ResultMessage)
  - `RemoteOutput` and `Output` does not have response.

## Result Messages

```python
class ReactiveResult(IntEnum):
    Ok                  = 0x0
    IllegalCommand      = 0x1
    IllegalPayload      = 0x2
    InternalError       = 0x3
    BadRequest          = 0x4
    CryptoError         = 0x5
    GenericError        = 0x6
```
