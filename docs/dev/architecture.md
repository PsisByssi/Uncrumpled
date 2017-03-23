

# DOCUMENT OUT OF DATE!

Uncrumpled implements the frontend and backend in python
I have split the logic as much as possible.

Maybe in the future the core could be in a different language communicating over rpc.
Because we are not using rpc, the gui has a reference to the app
the app COULD also have a reference to the gui for bidirectional calling.

# The Core

The core relies on the database, uncrumpled is all about storing user
settings and configurations and operating on them. It might be possible
to seperate this layer, but it maps really well into our database, and seems pointless to do so.
The only benifet would be faster tests, which is a mute point because we will change
the core to a different language if uncrumpled becomes successfuly anyway.

Profile -> spin off and make a seperate program
Book ->
Page ->
Hotkey ->

# The Presenter

The presenter is a little bit special in that it does more than just talking
the the ui and core.

Inspired by lighttable (see the ide as a value blog post), we store all
state in a dictionary. This has currently no purpose or value.
This will be used later to make settings and options, everything configurable
to users and plugins.

The presenter takes a requests, gets the response, and where appropriate modifies
the system, finally it sends a response back for the ui, which will run
the function and do some action.


# Architecture

We are trying to follow the clean architecture. (more in the large)
* http://www.slideshare.net/andbed/clean-architecture
* http://fernandocejas.com/2014/09/03/architecting-android-the-clean-way/

Here is a small flow chart of user interactions
The layers at the top don't know about the layers above.

also we only pass data around to the different layers

uncrumpled/main.py -> kivygui/toplevel.py starts gui
{user clicks} kivygui/xyz.py (view) -> kivygui/presenter/request.py (presenter)
request.py -> unc/presenter/presenter.py (boundary/interface)
presetner.py-> unc/core/requests/xyz.py (interactor)
requests.py -> unc/core/dbapi/xyz.py etc (entities)

{response} unc/presenter/presenter.py -> unc/presenter/response.py
unc/presenter/response.py -> unc/core/response.py
unc/presenter/responses.py -> kivygui/presenter/response.py
kivygui/presenter/response.py -> kivygui/xyz.py

## Database
unc/core/requests/xyz.py (interactor) -> unc/dbapi/dbapi.py

## neovim

unc/ui/ handles the interaction with neovim




# Ux

## Design Ideas
* https://www.sitepoint.com/sitepoint-smackdown-atom-vs-brackets-vs-light-table-vs-sublime-text/
* https://www.elegantthemes.com/blog/resources/10-rules-of-good-ui-design-to-follow-on-every-web-design-project

# Setup

`pip install -r requirements.txt` should be pretty good
all my dev stuff has to be done manually with `pip install -e`
also now /unc and /tkgui have to be installed as packages

# Other cool apps
https://gingkoapp.com/

# Api Design
http://stackoverflow.com/questions/6022074/api-design-python

# Links for names
http://wordsmith.org/anagram/anagram.cgi?anagram=carnet%2C&t=1000&a=n
http://online.ectaco.com/main.jsp;jsessionid=bc30bfd809a1366225e3?do=e-services-dictionaries-word_translate1&direction=1&status=translate&lang1=23&lang2=ml&source=notebook


# How Uncrumpled will now work

1. Opening uncrumped can be used as a scratch pad.

Notes will be created loosley, they require a name on saving.

2. Opening another txt file will import that file into uncrumped
as a loose page.

3. Uncrumpled can always be open in loose mode by?

4. Uncrumpled can make a new project on the fly by doing?

5. Uncrumpled can make a new hotkey bind on the fly?

open uncrumpled -> newbook hotkey-> follow prompts ->

default book behvaiour is too show the last use page in that
workbook

books act then as a vim instance.

6. Uncrumpled can view notes by?
