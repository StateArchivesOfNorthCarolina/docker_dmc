# Ideas for Future Work


- Consider a function to self-determine if the account directory is EML or MOX and validate the structure before proceeding to create an EAXS.
	- This is especially important because, when using the sample EML data in `./tests/sample_files`, an XSD-valid EAXS is created regardless of whether or not the `from_eml` flag is used.
	- On a related note, the existing MBOX structure validator was disabled for the current version of the software because it followed assumptions made by the original CmdDArcMailXml.py tool. Many of those assumptions may no longer be valid within the current version's context.