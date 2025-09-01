import threading

def ask_confirmation(queries, timeout=10, max_preview=20):
    """
    Show a preview of queries and ask for user confirmation.
    Accepts Y/y or N/n. Timeout defaults to 'Yes'.
    If queries are too many, only the first `max_preview` are shown.
    """
    print("\n🔍 The following queries will be executed:")

    if len(queries) > max_preview:
        for q in queries[:max_preview]:
            print(f" - {q}")
        print(f" ...and {len(queries) - max_preview} more queries not shown.")
    else:
        for q in queries:
            print(f" - {q}")

    answer = [None]  # mutable container to store the user's answer

    def user_input():
        ans = input(f"\nDo you want to proceed? (Y/N) [default Y in {timeout}s]: ").strip()
        if ans in ["Y", "y", "N", "n"]:
            answer[0] = ans.upper()

    # Start input in a separate thread
    thread = threading.Thread(target=user_input)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if answer[0] is None:
        print("\n⏱ Timeout reached. Assuming 'Yes'.")
        return True

    return answer[0] == "Y"
