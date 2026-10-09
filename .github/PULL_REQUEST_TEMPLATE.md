## HN BlackBox change

### What changed?
- 

### Why?
- 

### Verification
- [ ] `python -m compileall -q core gui ui`
- [ ] `python -m pytest -q`
- [ ] Renderer syntax checked (`node --check renderer/src/main.js`)
- [ ] No cryptographic implementation behavior changed unintentionally

### UI / runtime notes
- [ ] Autonomous animation remains independent of hover/focus
- [ ] Heavy rendering remains outside the Tk event loop where applicable
- [ ] No new secrets, credentials, or local machine paths committed
