
helptext = """
    Rollbot implements the /roll, /distribution and /list command.
    Please go to [tmiedema.com/rollbot](https://tmiedema.com/rollbot) to learn more
    Rollbot has the following functionality:
        roll examples: d20, 8d8
        keep highest: 3d20k2, 4d6k3
        math operators: +,-,\\*,/,%
        logical operators: >, <, ==
        functions:
            max(a,b,..): take the maximum of a set
            min(a,b,..): take the minimum of a set
            fac(a): compute the factorial
            comb(a,b): compute the comination
            any(a,b,c): return 1 if any argument is > 0
        assignment:
            macro assignment: creates a variable that will reroll
                              contained dice every time it is referenced
            examples: a = 2d20, b=d8+3
            value assignment: compute the result of a diceroll and assign it
                              to a variable.
            examples: a &= 2d20
        multirolls:
            You can combine multiple actions into one roll and even assign
            those to macros.
            examples: d20; d20+7
                      reroll_1s_d6 = (d6; a &= (a == 1) * d6 + (a > 1) * a; a)
        comments:
            You can apply text commentary on statements
            examples: "This is a roll:" d20; "And another one" d100+20
"""


update_text = """
    Rollbot has migrated to discord slash commands. The old message
    intents in discord will no longer work, see [here](https://discord.com/blog/slash-commands-are-here).
    Use /roll from now on. This message will only be shown once.
    You might need to re-invite the bot to get the slash commands to work. You can do that [here](https://discord.com/api/oauth2/authorize?client_id=712234733542572063&permissions=2147534848&scope=bot%20applications.commands).
"""


welcome_text = """
    Rollbot supports Discord slash commands. Use /roll and /distribution to roll dice.
    If you need any help, check out [the website](https://tmiedema.com/rollbot)! You can find a
    bunch of links there, also including a link to the source code if you are interested.
    Suggestions for improvements are also very welcome!
"""
