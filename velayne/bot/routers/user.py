@router.message(Command("payment_status"))
async def payment_status_cmd(m: Message):
    args = m.text.split()
    if len(args) < 2:
        await m.answer("Использование: /payment_status <код платежа>")
        return
    ext_id = args[1]
    from velayne.billing.yookassa import payment_status_handler
    await payment_status_handler(m, ext_id)