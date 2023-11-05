import contextlib
import random, os, asyncio
from . import *
from database.community import IntializeCommunity
from swibots import EmbeddedMedia, EmbedInlineField, InlineMarkupRemove
from PIL import Image
from typing import Optional, List, Tuple

GLOBAL = {}


class Card:
    suits = ["clubs", "diamonds", "hearts", "spades"]

    def __init__(self, suit: str, value: int, down=False):
        self.suit = suit
        self.value = value
        self.down = down
        self.symbol = self.name[0].upper()

    @property
    def name(self) -> str:
        """The name of the card value."""
        if self.value <= 10:
            return str(self.value)
        else:
            return {
                11: "jack",
                12: "queen",
                13: "king",
                14: "ace",
            }[self.value]

    @property
    def image(self):
        return (
            "red_back.png"
            if self.down
            else f"{self.symbol if self.name != '10' else '10'}"
            f"{self.suit[0].upper()}.png"
        )

    def flip(self):
        self.down = not self.down
        return self

    def __str__(self) -> str:
        return f"{self.name.title()} of {self.suit.title()}"

    def __repr__(self) -> str:
        return str(self)


def calc_hand(hand: List[List[Card]]) -> int:
    """Calculates the sum of the card values and accounts for aces"""
    non_aces = [c for c in hand if c.symbol != "A"]
    aces = [c for c in hand if c.symbol == "A"]
    sum = 0
    for card in non_aces:
        if not card.down:
            sum += 10 if card.symbol in "JQK" else card.value
    for card in aces:
        if not card.down:
            sum += 11 if sum <= 10 else 1
    return sum


def center(*hands: Tuple[Image.Image]) -> Image.Image:
    """Creates blackjack table with cards placed"""
    bg: Image.Image = Image.open(
        # os.path.join(ABS_PATH, 'modules/', 'table.png')
        "assets/table.png"
    )
    bg_center_x = bg.size[0] // 2
    bg_center_y = bg.size[1] // 2

    img_w = hands[0][0].size[0]
    img_h = hands[0][0].size[1]

    start_y = bg_center_y - (((len(hands) * img_h) + ((len(hands) - 1) * 15)) // 2)
    for hand in hands:
        start_x = bg_center_x - (((len(hand) * img_w) + ((len(hand) - 1) * 10)) // 2)
        for card in hand:
            bg.alpha_composite(card, (start_x, start_y))
            start_x += img_w + 10
        start_y += img_h + 15
    return bg


def hand_to_images(hand: List[Card]) -> List[Image.Image]:
    return [Image.open(os.path.join("./assets/cards/", card.image)) for card in hand]


@app.on_command("blackjack")
async def blackjack(ctx: BotContext[CommandEvent]):
    com = None
    bet = ctx.event.params
    event = ctx.event.message
    if bet:
        try:
            bet = int(bet)
        except ValueError:
            return await ctx.event.message.reply_text("Invalid Bet amount!")

    if event.community_id:
        com = IntializeCommunity(event.community_id)
        if com._com.child("economy").get():  # Economy is enabled
            credit = com.get_user_credit(event.user_id)
            if not bet:
                return await event.reply_text(
                    f"Provide the bet amount!\nYour credits: {credit}"
                )
            if not (0 < bet <= credit):
                return await event.reply_text("Invalid bet amount!")

    if not bet:
        bet = 1
    deck = [Card(suit, num) for num in range(2, 15) for suit in Card.suits]
    random.shuffle(deck)  # Generate deck and shuffle it

    player_hand: List[Card] = []
    dealer_hand: List[Card] = []

    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop())
    player_hand.append(deck.pop())
    dealer_hand.append(deck.pop().flip())

    player_score = calc_hand(player_hand)
    dealer_score = calc_hand(dealer_hand)

    def output(name, *hands: Tuple[List[Card]]) -> None:
        center(*map(hand_to_images, hands)).save(f"{name}.png")

    async def out_table(msg, inline_markup=None, **kwargs) -> Message:
        """Sends a picture of the current table"""
        output(ctx.event.user.id, dealer_hand, player_hand)
        embed = EmbeddedMedia(
            thumbnail=f"{ctx.event.message.user_id}.png",
            **kwargs,
        )
        if msg:
            msg = await msg.edit_text(
                "Blackjack", embed_message=embed, inline_markup=inline_markup
            )
        else:
            msg = await ctx.event.message.send(
                "BlackJack", embed_message=embed, inline_markup=inline_markup
            )
        return msg

    standing = False

    msg = None
    while True:
        player_score = calc_hand(player_hand)
        dealer_score = calc_hand(dealer_hand)
        if player_score == 21:  # win condition
            bet = int(bet * 1.5)
            if com:
                com.add_economy_credit(event.user_id, bet)
            result = ("Blackjack!", "won")
            break
        elif player_score > 21:  # losing condition
            if com:
                com.reduce_economy_credit(event.user_id, bet)
            result = ("Player busts", "lost")
            break
        #        if msg:
        #           await msg.delete()
        msg_id = ctx.event.message.id
        msg = await out_table(
            msg,
            title="Your Turn",
            description=f"Your hand: {player_score}\n" f"Dealer's hand: {dealer_score}",
            inline_fields=[[EmbedInlineField("", "", "Output")]],
            header_name="Blackjack",
            header_icon="https://img.icons8.com/?size=512&id=BdrGOzAgTJx3&format=png",
            footer_icon="https://img.icons8.com/?size=512&id=BdrGOzAgTJx3&format=png",
            footer_title="Continue playing..",
            inline_markup=InlineMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Hit", callback_data=f"blkj_H_{msg_id}_{ctx.event.user_id}"
                        ),
                        InlineKeyboardButton(
                            "Stand",
                            callback_data=f"blkj_S_{msg_id}_{ctx.event.user_id}",
                        ),
                    ]
                ]
            ),
        )
        if not GLOBAL.get(event.user_id):
            GLOBAL[event.user_id] = {}
        GLOBAL[event.user_id][msg_id] = None

        async def getClick():
            while not GLOBAL.get(event.user_id, {}).get(msg_id):
                await asyncio.sleep(0.05)

        try:
            task = asyncio.create_task(getClick())
            await asyncio.wait_for(task, timeout=60 * 3)
        except asyncio.TimeoutError:
            with contextlib.suppress(KeyError):
                del GLOBAL[event.user_id][msg_id]
            await msg.delete()
            return
        option = GLOBAL[event.user_id][msg_id]
        if option == "H":
            player_hand.append(deck.pop())
            continue
        elif option == "S":
            standing = True
            with contextlib.suppress(KeyError):
                del GLOBAL[event.user_id][msg_id]
            break

    if standing:
        dealer_hand[1].flip()
        player_score = calc_hand(player_hand)
        dealer_score = calc_hand(dealer_hand)

        while dealer_score < 17:  # dealer draws until 17 or greater
            dealer_hand.append(deck.pop())
            dealer_score = calc_hand(dealer_hand)

        if dealer_score == 21:  # winning/losing conditions
            if com:
                com.add_economy_credit(event.user_id, bet * -1)
            result = ("Dealer blackjack", "lost")
        elif dealer_score > 21:
            if com:
                com.add_economy_credit(event.user_id, bet)
            result = ("Dealer busts", "won")
        elif dealer_score == player_score:
            result = ("Tie!", "kept")
        elif dealer_score > player_score:
            if com:
                com.add_economy_credit(event.user_id, bet * -1)
            result = ("You lose!", "lost")
        elif dealer_score < player_score:
            if com:
                com.add_economy_credit(event.user_id, bet)
            result = ("You win!", "won")
    with contextlib.suppress(KeyError):
        del GLOBAL[event.user_id][ctx.event.message_id]
    msg = await out_table(
        msg,
        inline_markup=InlineMarkupRemove(),
        title=result[0],
        description=(
            f"**You {result[1]} ${bet}**\nYour hand: {player_score}\n"
            + f"Dealer's hand: {dealer_score}"
        ),
        header_name="Blackjack",
        header_icon="https://img.icons8.com/?size=512&id=BdrGOzAgTJx3&format=png",
        footer_icon="https://img.icons8.com/?size=512&id=BdrGOzAgTJx3&format=png",
        footer_title="Play again!",
        inline_fields=[[EmbedInlineField("", "", "Output")]],
    )
    os.remove(f"./{ctx.event.user_id}.png")


@app.on_callback_query(regexp(r"blkj_(.*)"))
async def oncall(e: BotContext[CallbackQueryEvent]):
    query = e.event.callback_data
    userAction = int(e.event.action_by_id)
    input = query.split("_")
    option = input[1]
    msgId = int(input[2])
    userId = int(input[3])
    if not GLOBAL.get(userAction) or userId != userAction:
        return
    GLOBAL[userAction][msgId] = option
