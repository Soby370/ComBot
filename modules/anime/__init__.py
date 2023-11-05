import requests
from .. import *
from typing import Dict


async def sendCharacter(data: Dict, message: Message, title: str, footer_title: str):
    await message.send(
        "*Character*",
        embed_message=EmbeddedMedia(
            thumbnail=data["images"]["jpg"]["image_url"],
            header_name=data["name"],
            description=f"Character Info of {data['name']}",
            header_icon="https://img.icons8.com/?size=256&id=63308&format=png",
            title=title,
            footer_title=footer_title,
            footer_icon="https://img.icons8.com/?size=256&id=20749&format=png",
            inline_fields=[[]],
        ),
    )


async def sendEmbedAnime(data: Dict, message: Message, title: str, footer_title: str):
    fields = [
        [
            EmbedInlineField(
                "https://img.icons8.com/?size=256&id=lBuKAleClNPO&format=png",
                data["title"],
                "Name",
            )
        ],
        [
            EmbedInlineField(
                "https://img.icons8.com/?size=256&id=eO0hZaSiMCsH&format=png",
                data.get("episodes"),
                "Episodes",
            )
            if data.get("episodes")
            else None,
            EmbedInlineField(
                "https://img.icons8.com/?size=256&id=8uAtuJQJ4jhd&format=png",
                data["score"],
                "Score",
            )
            if data.get("score")
            else None,
        ],
        [
            EmbedInlineField(
                "https://img.icons8.com/?size=256&id=JrbE13EfhZWo&format=png",
                data["duration"],
                "Duration",
            )
            if data.get("duration")
            else None,
            EmbedInlineField(
                "https://img.icons8.com/?size=50&id=wQ15B9zLAw61&format=png",
                data["year"],
                "Year",
            )
            if data.get("year")
            else None,
        ],
        [
            EmbedInlineField(
                "https://img.icons8.com/?size=256&id=runYFO7RVbcD&format=png",
                data["rating"],
                "Rating",
            )
            if data.get("rating")
            else None
        ],
    ]
    if value := ", ".join(map(lambda x: x["name"], data["genres"])):
        fields.append(
            [
                EmbedInlineField(
                    "https://img.icons8.com/?size=256&id=lLPVRq5v9Szf&format=png",
                    value,
                    "Genres",
                )
            ],
        )

    await message.send(
        "Anime",
        embed_message=EmbeddedMedia(
            thumbnail=data.get("images", {}).get("jpg", {}).get("large_image_url"),
            title=title,
            header_name=data.get("title"),
            footer_title=footer_title,
            inline_fields=fields,
            description=data.get("synopsis", "Anime"),
            header_icon="https://img.icons8.com/?size=256&id=zYzYv8aFrMIB&format=png",
            footer_icon="https://img.icons8.com/?size=256&id=p3miLroKw4iR&format=png",
        ),
    )
