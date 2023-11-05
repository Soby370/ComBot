import sys, io, traceback
from . import *


@Bot.on_command("eval", filters.user(Config.OWNER_ID))
async def runEval(ctx: BotContext[CommandEvent]):
    message = ctx.event.message
    param = ctx.event.params
    if not param:
        return await message.reply_text("Provide command to run!")

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(param, app, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = (
        f"<b>EVAL</b>: <copy>{param}</copy>\n\n<b>OUTPUT</b>:\n<copy>{evaluation.strip()}</copy> \n"
    )
    await message.reply_text(final_output)


async def aexec(code, client, message):
    exec(
        f"async def __aexec(app, message): "
        + "".join(f"\n {l}" for l in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)
