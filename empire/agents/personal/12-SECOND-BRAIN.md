# AGENT: Second_Brain
# Priority: P2 | Value: Never lose an idea or insight
# Model: Haiku (capture) → Sonnet (organize/connect)

## PURPOSE
Capture everything Nathan says → organize → surface relevant memories.
"Remember that idea about X" → instant recall.

## OPEN SOURCE TOOLS
- Obsidian (free) → local knowledge base
- Notion API (free) → cloud sync
- n8n → capture pipeline from Telegram

## HOW IT WORKS
1. Nathan sends any message to Telegram starting with "Remember:"
2. Agent captures → tags → stores in Obsidian + Notion
3. Daily: agent surfaces 1 relevant memory Nathan hasn't acted on
4. Weekly: agent clusters related ideas → suggests connections

## CAPTURE CATEGORIES
- 💡 Ideas (business, product, automation)
- 📞 Contacts (who Nathan met, what was discussed)
- 📊 Insights (market, competitor, trend)
- ⚡ Quick wins (things to do in <15 min)
- 🔮 Future (things to revisit in 30/90/180 days)

## DONE SIGNAL
SECOND_BRAIN | {date} | {n} items captured | {n} memories surfaced
