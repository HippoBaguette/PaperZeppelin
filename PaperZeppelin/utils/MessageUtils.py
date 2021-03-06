import datetime
import typing
import discord
from discord.activity import Activity, BaseActivity
from discord.ext import commands
from discord.ext.commands.help import HelpCommand


async def gen_bot_help(help_command: HelpCommand, mapping) -> str:
    message = f"**Paper Zeppelin help 1/1**\n```diff\n"
    for cog in mapping:
        if cog is not None:
            filtered = await help_command.filter_commands(mapping[cog])
            commands = "\n".join(
                [
                    f"  {command.name}{' ' * (14 - len(command.name))}{command.short_doc}{help_command.is_group(command)}"
                    for command in filtered
                ]
            )
            if cog.qualified_name == "Basic":
                commands += (
                    "\n  help          List all commands, and get info on commands"
                    if cog.qualified_name == "Basic"
                    else ""
                )
            message += (
                f"- {cog.qualified_name}\n{commands}\n" if len(commands) > 0 else "\n"
            )
    message += f"You can get more info about a command (params and subcommands) by using '{help_command.context.clean_prefix}help <command>'\nCommands followed by ↪ have subcommands."
    message += "\n```"
    return message


async def gen_cog_help(help_command, cog) -> str:
    message = f"**Paper Zeppelin help 1/1**\n```diff\n- {cog.qualified_name}\n"
    filtered = await help_command.filter_commands(cog.get_commands())
    commands = "\n".join(
        [
            f"{command.name}{' ' * (14 - len(command.name))}{command.short_doc}{help_command.is_group(command)}"
            for command in filtered
        ]
    )
    commands += (
        "\nhelp          List all commands, and get info on commands\n"
        if cog.qualified_name == "Basic"
        else ""
    )
    message += f"{commands}\n"
    message += f"You can get more info about a command (params and subcommands) by using '{help_command.context.clean_prefix}help <command>'\nCommands followed by ↪ have subcommands."
    message += "\n```"
    return (
        message
        if len(filtered) > 0 or cog.qualified_name == "Basic"
        else "🔒 You do not have permission to view this cog"
    )


async def gen_group_help(help_command, group: commands.Group) -> str:
    message = f"**Paper Zeppelin help 1/1**\n```diff\n"
    filtered = await help_command.filter_commands(group.commands)
    message += f"{help_command.context.clean_prefix}{group.full_parent_name} [{group.name}{'|' + '|'.join(group.aliases) if len(group.aliases) > 0 else ''}]\n"
    message += f"\n{group.short_doc}\n"
    message += "\nSubcommands:\n"
    commands = "\n".join(
        [
            f"  {command.name}{' ' * (14 - len(command.name))}{command.short_doc}{help_command.is_group(command)}"
            for index, command in enumerate(group.commands)
        ]
    )
    message += f"{commands}\n"
    message += f"You can get more info about a command (params and subcommands) by using '{help_command.context.clean_prefix}help <command>'\nCommands followed by ↪ have subcommands."
    message += "\n```"
    return (
        message
        if len(filtered) > 0 or group.cog.qualified_name == "Basic"
        else "🔒 You do not have permission to view this command"
    )


async def gen_command_help(help_command, command) -> str:
    message = f"**Paper Zeppelin help 1/1**\n```diff\n"
    filtered = await help_command.filter_commands([command])
    commands = (
        f"{help_command.context.clean_prefix}  {command.name}\n\n{command.short_doc}"
    )
    message += f"{commands}\n"
    message += "\n```"
    return (
        message
        if len(filtered) > 0
        else "🔒 You do not have permission to view this command"
    )


def build(**kwargs):
    type = kwargs.get("type")
    if type is None:
        return "An internal error occured"
    else:
        if type == "user_info":
            return user_info(member=kwargs.get("member"), issuer=kwargs.get("issuer"))
        elif type == "status_update":
            return status_update(before=kwargs.get("before"), after=kwargs.get("after"))
        elif type == "presence_update":
            return presence_update(
                before=kwargs.get("before"), after=kwargs.get("after")
            )
        elif type == "verification_level":
            return verification_level(
                level=kwargs.get("level"), prefix=kwargs.get("prefix")
            )


def verification_level(level: int, prefix: str) -> str:
    if level == 0:
        return "There is currently no verification method set up for this server (use `{prefix}help cfg verification` to find out how to set it up)".format(
            prefix=prefix
        )
    elif level == 1:
        return "Current verification level: 1 (command)"


def user_info(
    member: typing.Union[discord.User, discord.Member], issuer: discord.User
) -> discord.Embed:
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    is_member = isinstance(member, discord.Member)

    embed = discord.Embed(
        colour=member.top_role.colour if is_member else 0x00CEA2, timestamp=now
    )
    embed.set_thumbnail(url=member.avatar.url)

    embed.add_field(
        name="Name", value=f"{member.name}#{member.discriminator}", inline=True
    )
    embed.add_field(name="ID", value=f"{member.id}", inline=True)
    embed.add_field(name="Bot account", value=f"{member.bot}", inline=True)
    embed.add_field(
        name="Animated avatar", value=f"{member.avatar.is_animated()}", inline=True
    )
    embed.add_field(
        name="Avatar url", value=f"[Avatar url]({member.avatar.url})", inline=True
    )
    embed.add_field(name="Profile", value=f"<@{member.id}>", inline=True)

    if is_member:
        embed.add_field(name="Nickname", value=member.nick, inline=False)
    if is_member:
        role_list = [
            role.mention
            for role in reversed(member.roles)
            if role is not member.guild.default_role
        ]
        if len(role_list) > 40:
            embed.add_field(name="Roles", value="Too many roles!", inline=False)
        elif len(role_list) > 0:
            embed.add_field(name="Roles", value=" ".join(role_list), inline=False)
        else:
            embed.add_field(name="Roles", value="No roles", inline=False)

    if is_member:
        embed.add_field(
            name="Joined at",
            value=f"{(now - member.joined_at).days} days ago, (``{member.joined_at}+00:00``)",
            inline=True,
        )

    embed.add_field(
        name="Created at",
        value=f"{(now - member.created_at).days} days ago, (``{member.created_at}+00:00``)",
        inline=True,
    )

    embed.set_footer(text=f"Requested by {issuer.name}", icon_url=issuer.avatar.url)
    return embed


def status_update(before: str, after: str) -> discord.Embed:
    embed = discord.Embed(
        color=0xE67E22,
        timestamp=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
        description=f"```Updated status```",
    )
    embed.add_field(name="Before", value=before)
    embed.add_field(name="After", value=after)
    return embed


def presence_update(before: str, after: Activity) -> discord.Embed:
    embed = discord.Embed(
        color=0xE67E22,
        timestamp=datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc),
        description=f"```Updated activity```",
    )
    embed.add_field(name="Before", value=before)
    embed.add_field(name="After", value=f"`{after.type}` {after.name}")
    return embed
