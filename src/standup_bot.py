import random
from typing import List, Optional

from discord import (
    Client,
    Embed,
    Guild,
    Intents,
    Interaction,
    Member,
    VoiceChannel,
    VoiceState,
    app_commands,
)


class StandupBot(Client):
    def __init__(self, guild_id: int, intents: Intents):
        super().__init__(intents=intents)
        self.tree: app_commands.CommandTree = app_commands.CommandTree(self)
        self._guild_id: int = guild_id

        self._guild: Optional[Guild] = None

        # The active channel in which standup is taking place
        self._channel: Optional[VoiceChannel] = None
        self._members_in_server: List[Member] = []
        self._members_here: List[Member] = []
        self._members_been: List[Member] = []

    @property
    def guild(self) -> Optional[Guild]:
        return self._guild

    @property
    def channel(self) -> Optional[VoiceChannel]:
        return self._channel

    @property
    def is_standup_taking_place(self) -> bool:
        return self._channel is not None

    async def on_ready(self):
        print(f"StandupBot ready!")

    async def setup_hook(self):
        self._guild = await self.fetch_guild(self._guild_id)

        print(f"Synching commands with Discord Server/Guild {self.guild.id}")
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def start_standup(self, interaction: Interaction):
        interaction_channel = interaction.channel
        if not isinstance(interaction_channel, VoiceChannel):
            await interaction.response.send_message(
                "❌ You can't start standup in a text channel!"
            )
            return

        self._channel = interaction_channel

        await self.update_members_in_server()
        await self.update_members_here()

        embed: Optional[Embed] = self.create_embed()
        if embed:
            await interaction.response.send_message(embed=embed)

    async def end_standup(self, interaction: Interaction):
        if interaction.channel != self.channel:
            await interaction.response.send_message(
                f"❌ There is no standup happening in {interaction.channel.name}."
            )
            return

        await self.end_standup_in_channel(interaction.channel)

        await interaction.response.send_message(
            f"🔇 Ended standup in {interaction.channel.name}."
        )

    async def end_standup_in_channel(self, channel: VoiceChannel):
        self._channel = None
        self._members_in_server = []
        self._members_here = []
        self._members_been = []

        await channel.send(f"🔇 Ended standup in {channel.name}.")

    async def member_been(self, interaction: Interaction, member: Member):
        if not self.is_standup_taking_place:
            await interaction.response.send_message(
                f"❌ There is no standup happening in {interaction.channel}."
            )
            return

        self._members_been.append(member)

        members_remaining: List[Member] = list(
            set(self._members_here).difference(set(self._members_been))
        )
        if members_remaining:
            next_member: Member = random.choice(members_remaining)
            await interaction.response.send_message(
                content=f"Next up... {next_member.mention}!"
            )
        else:
            await interaction.response.send_message(content=f"Everyone here has been!")

        embed: Optional[Embed] = self.create_embed()
        if embed:
            await self._channel.send(embed=embed)

    def create_embed(self) -> Optional[Embed]:
        if not self.is_standup_taking_place:
            return None

        embed: Embed = Embed(title=f"🔊 STANDUP ({self.channel.name})", type="rich")

        for member in self._members_in_server:
            is_member_here: bool = member in self._members_here
            has_member_been: bool = member in self._members_been

            value: str = f"Here? {self.pretty_bool(is_member_here)} Been? {self.pretty_bool(has_member_been)}"

            embed.add_field(name=member.name, value=value, inline=False)

        return embed

    def pretty_bool(self, value: bool) -> str:
        return "✅" if value else "❌"

    async def update_members_here(self) -> None:
        if self._channel:
            self._members_here = self._channel.members
        else:
            self._members_here = []

        if len(self._members_here) == 0:
            self.end_standup_in_channel(self._channel)

    async def update_members_in_server(self) -> None:
        self._members_in_server = []

        async for member in self.guild.fetch_members():
            if not member.bot:
                self._members_in_server.append(member)

        self._members_in_server.sort(key=lambda x: x.name)

    # Called when a Member changes their voice state, for example, by joining or
    # leaving a voice channel
    async def on_voice_state_update(
        self,
        member: Member,
        before: VoiceState,
        after: VoiceState,
    ):
        if not self.is_standup_taking_place:
            return

        channel_before: Optional[VoiceChannel] = before.channel
        channel_after: Optional[VoiceChannel] = after.channel

        if channel_before != channel_after and channel_after is not None:
            await channel_after.send(f"✅ {member.name} joined {channel_after.mention}")
            await self.update_members_here()
            embed: Optional[Embed] = self.create_embed()
            if embed:
                await channel_after.send(embed=embed)

        if channel_before != channel_after and channel_before is not None:
            await channel_before.send(f"🚫 {member.name} left {channel_before.mention}")
            await self.update_members_here()
            embed: Optional[Embed] = self.create_embed()
            if embed:
                await channel_before.send(embed=embed)
