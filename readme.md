# Device Instruction Transmission Protocol (DIT)

DIT is a protocol that allows a users to query devices about specific data. This protocol allows for expansion on what can be requested

All data is encrypted with a symmetric encryption, this key also acts as authentication between the server and client. It also allows for a second authentication with a password, so that if the key is stolen the user still needs a password to perform a command, though if on the same network other messages can be decrypted and the hash repeated, I have plans to fix this