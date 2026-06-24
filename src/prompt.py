"""Fixed non-interactive Claude CLI instructions."""

INVOCATION_PREAMBLE = """
# ai-servant invocation

You are running in non-interactive mode.
Do not ask the user questions.
Do not wait for user input.
Complete the tasks using the available Claude CLI capabilities.
If the tasks cannot be completed without asking, stop and print the reason.
Follow the current Claude CLI permission settings.
If Claude CLI refuses an operation, do not bypass it.
"""
