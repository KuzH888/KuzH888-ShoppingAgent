# Prototype Runtime Check

Date: 2026-09-10  
Mode: local simulation (no API key used)

## Startup and shutdown

- `scripts/start.ps1 -NoBrowser` started FastAPI on port 8000 and Vite on port 5173.
- `scripts/check.ps1` confirmed backend health, frontend availability, catalogue, model list, policies and assistant comparison.
- `scripts/stop.ps1` stopped the tracked frontend and backend root/listener processes.
- Both ports were confirmed free after shutdown.
- The project was started again successfully and left available for inspection.

## Browser workflow

- Storefront loaded 24 products.
- Product detail drawer opened and closed successfully.
- Two products were selected and displayed in the comparison dialog.
- Chinese shopping request returned `DIG-001` as the grounded local recommendation.
- Returns-policy question returned the validated 30-day simulated policy.
- Model selector changed from Luna to Terra and back to Luna.
- Browser console reported zero warnings and errors during the final run.

## Automated verification

- Python: 27 tests passed.
- Frontend: 4 tests passed.
- TypeScript and Vite production build passed.

## Boundary

This check proves that the offline prototype runs end to end. It does not claim that live OpenAI access works; live-provider verification remains a later step.
