messages = {}

# Add the first user message and bot response
messages.update({"user_msg": ['sdsdsd']})
messages.update({"bot_response": ['sdsdd76w78dyhwssd']})

# Add the second user message without updating the previous value
if "user_msg" in messages:
    messages["user_msg"].append('sdsdsdsds33sd')
else:
    messages.update({"user_msg": ['sdsdsdsds33sd']})

print(messages)
