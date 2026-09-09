# Project Readiness Review

## Current status

The project is ready for catalogue customisation. Its backend, frontend, local simulation, product tools, policy tools and offline evaluation pipeline are implemented. Real LLM testing and the final evaluation are intentionally deferred until the user finishes replacing products and product images.

## Completed checks

- FastAPI and Vue applications communicate through typed JSON endpoints.
- Product facts are loaded from validated local data instead of being invented by the model.
- Recommendation rules preserve stock, product type, budget, required features and exclusions.
- Product details, two-to-three-product comparison and policy lookup work in simulation mode.
- The model selector is populated from a server-side allow-list; the API key remains server-side.
- Automated Python and frontend tests are available.
- The development evaluation records a catalogue SHA-256 fingerprint to prevent stale results from being presented as final.

## Known boundaries

- The store contains fictional demonstration products and does not process real orders.
- The current evaluation is an offline development baseline, not a live-LLM quality score.
- Product image paths are reserved in the catalogue, but the user will choose and replace the final product images before the image rendering workflow is finalised.
- The two dependency deprecation warnings reported by the Python test suite originate from the installed FastAPI/Starlette testing stack and do not fail the tests.

## Required before final submission

1. Replace and validate the product catalogue and images.
2. Review and update expected results in both evaluation JSON files.
3. Run the full Python and frontend test suites.
4. Configure the API key locally and run a small set of live-model tests.
5. Generate `outputs/evaluation_report.md` with the final catalogue.
6. Add final screenshots and complete the author fields in README and Notebook.
