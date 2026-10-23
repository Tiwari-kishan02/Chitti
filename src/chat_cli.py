from brain import respond

print("Chitti CLI. Type 'exit' to quit.")
while True:
    msg = input("You: ").strip()
    if msg.lower() in ("exit", "quit"):
        break
    if not msg:
        continue
    r = respond(msg)
    print("Chitti:", r["reply"])
    if r["notes"]:
        print("   ->", r["notes"])
    print("   [intent:", r["intent"], "]")