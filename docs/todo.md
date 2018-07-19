# Ideas for Future Work

- Improve documentation of sub-modules and remove legacy code or objects that are no longer used.
 
- Consider adding back the JSON EAXS output option. This is disabled in the current version because it isn't working correctly for MBOX and appears to not work at all for EML.

- The `_devel` and `_tomes_tool` class attributes are specific to the Docker version of the software and should not be part of the main class. If there are values that need to be altered in order for the module to work in Docker, they can be altered once the class is instantiated in the Docker version.

- MBOX validation has been disabled, but we should consider adding a method that will determine on its own whether the structure is MBOX or EML. This should include support for EML files without ".eml" extensions as with the Enron dataset. Validation could be automatically or optionally performed once the type of structure is determined.

- Reconsider `lib/xml_help/CommonMethods.py`. Specifically, we should avoid the use of globals.

