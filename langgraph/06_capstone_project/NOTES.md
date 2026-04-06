# Learning Notes — Capstone Project (Section 06)

## What clicked for me
> [Write what made sense about combining all concepts into one agent]

## What confused me
> [Write any concepts that were unclear]

## Key mental models I built
- [ ] I can structure a multi-file LangGraph project
- [ ] I understand how all concepts fit together in one agent
- [ ] I can explain the research agent's graph flow from start to finish
- [ ] I know what changes are needed for production deployment

## Architecture Decisions
| Decision | Why |
|---|---|
| Separate state.py | Single source of truth for the state schema |
| Separate tools.py | Tools are independent and reusable |
| Separate nodes.py | Node logic is isolated from graph structure |
| Separate graph.py | Graph construction is independent of execution |

## What I Would Change in Production
1. Replace MemorySaver with MongoDBSaver
2. Add real search API (Tavily, SerpAPI)
3. Add error handling at each node
4. Add rate limiting for API calls
5. Add observability/logging
6. Add user authentication
7. Deploy as a FastAPI service

## Experiments I tried
> [What happened when you modified the graph? Added a new tool? Changed the routing?]

## Questions I still have
> [Write any lingering questions here]
