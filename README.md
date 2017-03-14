# DarcMailCLI v0.8.0
This is a fork of Carl Shaefer's (Smithsonian Institution Archives) 
CmdDarcMailXml.  My goal with this refactor is to modularize the
tool, and add some functionality.

As of this version DarcMailCLI produces valid EAXS xml in a single 
file or multiple chunked files if the attachments are stored externally
(I have not tested the internal storage of attachments in the main xml file, 
because why?), with one exception.

The published schema requires that the OrigDate header be encoded as an 
XML dateTime.  While this is not impossible, there are significant 
archival issues at play here. This becomes the only field that is 
significantly transformed from its representation in 
the mbox.  

### For Example
Original Mbox
_Date: Tue, 4 Aug 2009 12:35:00 +2100_

XML
_<OrigDate>2009-08-04T12:35:00+21:00</OrigDate>_

The problem with this example is that +21:00 is not a valid XML 
dateTime range. It must be between +1400 and -1400.

We could normalize the dateTime object, but then we would have 
significantly altered the original field's value. The canonical way to
do this is to remove 21 hours from the Date Time.  So then, the representation
of the originally transmitted Date and Time becomes:

_<OrigDate>2009-08-03T15:35:00Z</OrigDate>_

Such a normalization is, I think, a bad idea.


*I believe the <OrigDate> should be a simple string value.* This most
accurately represents the original nature of the mbox.

I realize this is a bad place for discussions of archival best practice,
but shouldn't we be free to talk shop is all sorts of different places?

# Requirements
* Python 3
* lxml
* yaml

## Usage
DarcMailCLI.py -a [Name of Account] -d [Path to the MBOX structure] 
                -c [integer] Number of messages per file.
