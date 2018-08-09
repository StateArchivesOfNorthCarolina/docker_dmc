# Ideas for Future Work

- More in-line documentation and function docstrings are needed for library modules. Additionally, logging of exceptions in try/except blocks needs to be added and/or improved.
- Address lingering "TODO" statements in the code.
- Consider a function to self-determine if the account directory is EML or MOX and validate the structure before proceeding to create an EAXS.
	- This is especially important because, when using the sample EML data in `./tests/sample_files`, an XSD-valid EAXS is created regardless of whether or not the `from_eml` flag is used.
	- On a related note, the existing MBOX structure validator was disabled for the current version of the software because it followed assumptions made by the original CmdDArcMailXml.py tool. Many of those assumptions may no longer be valid within the current version's context.
- Currently, "empty" EAXS files will be created if DarcMail processes an EML folder with no `.eml` files. For future versions, no EAXS file or folder structure should be created if no actual EML or MBOX data is found.
- The use of globals in modules such as  `./tomes_darcmail/lib/xml_help/CommonMethods.py` should be avoided in future versions.
- The `_devel` parameter should be removed as it only appears to set a Windows-style path for testing purposes. A test directory can just be passed as the output directory for any testing needs.
- Investigate the rationale for the `_tomes_tool` parameter in terms of what behaviors it changes in terms of running within a Docker container. There may be a better way to handle this issue without having conditional behavior based on this parameter. 
- Consider adding the option to output EAXS files per message using the same path structure as EML. This will allow for a more sustainable approach to updating the status of individual messages over time and falls more in line with the concept of "iterative processing".
