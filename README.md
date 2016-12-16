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

github webhook integration
--------------------------

This script can be automatically called using github webhook. For this you need
a machine with public IP, preferably running Qubes OS (but it isn't strictly
required).

1. Setup HTTP server in `sys-net`, configure it to execute CGI scripts from
   selected directory, put `github-webhook` script there. You may want to use
   [bind-dirs][https://www.qubes-os.org/doc/bind-dirs/] feature to make its
   configuration persistent. You'll also need to allow incoming traffic on
   firewall there.
2. Create a VM where you'll run `check-sig-signature` script. This VM will have
   access to your Github API token. For the sake of example, lets call it `sig-check`
3. Copy `qubes-rpc/qubesinfra.CheckPRSignature` to
   `/usr/local/etc/qubes-rpc/qubesinfra.CheckPRSignature` there.
4. Copy `check-git-signature` to `/home/user/bin/check-git-signature` there.
5. Create `/home/user/.config/qubes/signature-checker` config file like this:

        [DEFAULT]
        # place actual token value here
        github_api_token = 01234567890123456782345678abcdef
        # whitelist repository owners (space-separated list)
        owner_whitelist = QubesOS
        # allow only selected repositories (space-separated list)
        #repo_whitelist = ...
        # exclude some repositories (space-separated list)
        #repo_blacklist = ...
        # allow only signatures made with keys in this keyring (path to gpg keyring
        # file)
        #keyring = ...

6. Create service policy in dom0
   (`/etc/qubes-rpc/policy/qubesinfra.CheckPRSignature`). Adjust target VM
   name:

        sys-net dom0 allow,target=sig-check

7. Configure webhook in github settings (action `pull_request`). Point it at
   `github-webhook` script.


If the machine is not running Qubes OS, edit `github-webhook` script to call
`qubesinfra.CheckPRSignature` instead of `qrexec-client-vm`.
