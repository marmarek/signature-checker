check-git-signature script
--------------------------

The script is meant to do the actual check and possibly report verification
status to github. Just for github purposes it could use signature verification
status already provided by github (experimental API:
https://developer.github.com/changes/2016-04-04-git-signing-api-preview/), but
the check is done locally, so the script could be reused for policy enforcement
elsewhere too.

By default the script accepts any key (as long as it can find it on some
keyserver), but can be configured to trust only keys in selected
keyring.

See `check-git-signature --help` for details.

