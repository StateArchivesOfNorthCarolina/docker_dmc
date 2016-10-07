# DarcMailCLI
This is a fork of Carl Shaefer's (Smithsonian Institution Archives) CmdDarcMailXml.  My goal with this refactor is to modularize the
tool, and add some functionality.

This initial commit doesn't do anything except build an EAXS representation of an email as a series of classes, and move the attachments
out of the internal representation.  Final output of this tool will be a structure like this:

- MBOX_ROOT_DIR/
  - /attachments
    - UUID.xml
    - UUID(2).xml
    - (n)...
  - /xml
    - EAXS.xml
  - /metadata
    - error.log
    - info.log
    - stats.xml
