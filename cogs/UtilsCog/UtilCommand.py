import disnake
from disnake.ext import commands
from disnake import Embed
from disnake.ext.commands import Param, Option, OptionType

class UtilsCommandCog(commands.Cog, name="Utilities"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='Check the bot\'s latency.')
    async def ping_command(self, ctx):
        latency = round(self.bot.latency * 1000)  # Latency in milliseconds

        embed = Embed(
            title='Pong!',
            description=f'Latency: {latency}ms',
            color=disnake.Colour.blue()
        )

        await ctx.send(embed=embed)

    @commands.command(name='echo', help='Repeat a message.')
    async def echo_command(self, ctx, *, message: str):
        embed = Embed(
            title='Echoed Message',
            description=message,
            color=disnake.Colour.green()
        )

        await ctx.send(embed=embed)

    @commands.command(name='avatar', help='Get the avatar of a user.')
    async def avatar_command(self, ctx, user: disnake.User = None):
        target_user = user or ctx.author
        avatar_url = target_user.avatar.url if target_user.avatar else target_user.default_avatar.url

        embed = Embed(
            title=f"{target_user.display_name}'s Avatar",
            color=disnake.Colour.gold()
        )
        embed.set_image(url=avatar_url)

        await ctx.send(embed=embed)

    @commands.slash_command(name='serverinfo', help='Get information about the server.')
    async def server_info_command(self, ctx: SlashContext):
        guild = ctx.guild
        member_count = len(guild.members)
        channel_count = len(guild.channels)

        embed = Embed(
            title='Server Information',
            description=f"Server Name: {guild.name}\n"
                        f"Member Count: {member_count}\n"
                        f"Channel Count: {channel_count}",
            color=disnake.Colour.blue()
        )

        await ctx.send(embed=embed)

    @commands.slash_command(name='userinfo', help='Get information about a user.')
    async def user_info_command(self, ctx: SlashContext, user: disnake.User):
        embed = Embed(
            title='User Information',
            description=f"Username: {user.name}\n"
                        f"Discriminator: {user.discriminator}\n"
                        f"ID: {user.id}",
            color=disnake.Colour.green()
        )

        await ctx.send(embed=embed)

    @commands.slash_command(
        name="roleinfo",
        description="Get detailed information about a role."
    )
    async def roleinfo(
        self, 
        ctx: disnake.ApplicationCommandInteraction, 
        role: disnake.Role
    ):
        # Role color
        rgb = role.color.to_rgb()
        color_int = rgb[0] << 16 | rgb[1] << 8 | rgb[2]
        color_hex = f"#{color_int & 0xFFFFFF:06x}"

        # Role type
        role_type = "Unknown"
        if role.is_default():
            role_type = "Peasant"
        elif role.permissions.administrator:
            role_type = "Admin"
        elif role.permissions.manage_roles:
            role_type = "Mod"
        elif role.hoist:
            role_type = "Collectable"

        # Role permissions
        role_perms = f"```{role.permissions}```"

        # Embed creation
        embed = disnake.Embed(
            title=f"{role.name}'s Info",
            color=role.color.value,
            timestamp=disnake.utils.utcnow()
        )

        embed.add_field(name="Role Color", value=f"Hex: {color_hex}", inline=False)
        embed.add_field(name="Role Type", value=role_type, inline=False)
        embed.add_field(name="Role Permissions", value=role_perms, inline=False)

        # Thumbnail
        if role.icon:
            embed.set_thumbnail(url=role.icon.url)

        # Footer
        embed.set_footer(text=f"Role ID: {role.id} | Godku Utils")

        await ctx.send(embed=embed)
      
def setup(bot):
    bot.add_cog(UtilsCommandCog(bot))
