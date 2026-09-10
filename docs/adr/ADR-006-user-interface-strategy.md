# ADR-006: Keeping the interface dumb on purpose

**Status:** Locked

## The decision

The Streamlit app is just the front door. It lets people upload data, set things up, and see results. All the real analytical work happens in separate backend code that has nothing to do with the interface.

That separation means the backend can be tested, reused, or swapped into a different interface entirely, without touching a single line of analysis logic.
