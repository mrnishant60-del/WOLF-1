from discord.ext import commands


class WolfError(commands.CheckFailure):
    pass


class NotSetup(WolfError):
    def __init__(self):
        super().__init__(
            "This command requires you to have Wolf's private channel.\nKindly run `{ctx.prefix}setup` and try again."
        )


class NotPremiumGuild(WolfError):
    def __init__(self):
        super().__init__(
            "This command requires this server to be premium.\n\nCheckout Wolf Premium [here]({ctx.bot.prime_link})"
        )


class NotPremiumUser(WolfError):
    def __init__(self):
        super().__init__(
            "This command requires you to be a premium user.\nCheckout Wolf Premium [here]({ctx.bot.prime_link})"
        )


class NotPremiumUserOrGuild(WolfError):
    def __init__(self):
        super().__init__(
            "This feature requires either you or this server to have Wolf Premium.\nCheckout Wolf Premium [here]({ctx.bot.prime_link})"
        )


class InputError(WolfError):
    pass


class SMNotUsable(WolfError):
    def __init__(self):
        super().__init__("You need either the `scrims-mod` role or `Manage Server` permissions to use this command.")


class TMNotUsable(WolfError):
    def __init__(self):
        super().__init__("You need either the `tourney-mod` role or `Manage Server` permissions to use tourney manager.")


class PastTime(WolfError):
    def __init__(self):
        super().__init__(
            f"The time you entered seems to be in past.\n\nKindly try again, use times like: `tomorrow` , `friday 9pm`"
        )


TimeInPast = PastTime


class InvalidTime(WolfError):
    def __init__(self):
        super().__init__(f"The time you entered seems to be invalid.\n\nKindly try again.")
