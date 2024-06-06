import re

try:
    import weechat
except ImportError:
    print("This script must be run under WeeChat.")
    print("Get WeeChat now at: http://www.weechat.org/")


SCRIPT_NAME    = "nick_notes"
SCRIPT_AUTHOR  = "SnoopJ"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "MIT"
SCRIPT_DESC    = "Add notes about a nick next to their lines"

weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, '', 'utf-8')

# TODO:
# * support for servers, hostnames

NICK_NOTES = {}
for entry in weechat.config_get_plugin("nick_notes").split(','):
    nick, sep, note = entry.partition("=")
    NICK_NOTES[nick] = note


version = weechat.info_get("version_number", "") or 0
if int(version) < 0x00020800:
    msg = f"This plugin requires weechat >= 2.8, found version {version}"
    raise RuntimeError(msg)


def add_nick_notes(data: str, modifier: str, modifier_data: str, msg: str):
    # NOTE: this layout changed after weechat version 2.8
    plugin, buffer_name, rawtags = modifier_data.split(';', maxsplit=2)
    tags = rawtags.split(',')

    is_action = any(t == "irc_action" for t in tags)
    is_privmsg = any(t == "irc_privmsg" for t in tags)
    nick = next((t for t in tags if t.startswith("nick_")), "")[5:]

    if is_privmsg and nick in NICK_NOTES:
        idx = msg.index(nick)
        # Hardcoding this color bytes offset is not great but works on my machine ¯\_(ツ)_/¯
        colored_nick = msg[idx-4:idx] + nick

        if is_action:
            msg = re.sub("\S+" + re.escape(colored_nick), "", msg)
            result = "*\t" + NICK_NOTES[nick] + " " + colored_nick + msg
        else:
            msg = re.sub("\S+" + re.escape(nick), "", msg)
            result = NICK_NOTES[nick] + " " + colored_nick + msg

    else:
        # pass through unchanged
        result = msg

    return result


weechat.hook_modifier("weechat_print", "add_nick_notes", "")
